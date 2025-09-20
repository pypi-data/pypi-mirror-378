# Copyright 2025 Christ10-8
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# -*- coding: utf-8 -*-
"""
Cifrado por columna (AES-GCM) con side-cars para SURFRAME.
"""
from __future__ import annotations

import io
import json
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
from zipfile import ZipFile, ZIP_DEFLATED

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

CRYPTO_CONFIG_PATH = "config/crypto.json"
ENC_DIR = "enc"
NONCE_SIZE = 12  # bytes
SALT_SIZE = 16   # bytes


@dataclass
class CryptoMeta:
    algo: str
    kdf: str
    scrypt_n: int
    scrypt_r: int
    scrypt_p: int
    salt_hex: str
    columns: List[str]
    parts: Dict[str, List[str]]  # part_id -> [cols]

    def to_dict(self) -> dict:
        return {
            "version": 1,
            "algo": self.algo,
            "kdf": self.kdf,
            "scrypt": {
                "n": self.scrypt_n,
                "r": self.scrypt_r,
                "p": self.scrypt_p,
                "salt": self.salt_hex,
            },
            "nonce_size": NONCE_SIZE,
            "columns": self.columns,
            "parts": self.parts,
        }


# -------------------- helpers --------------------

def _derive_key(passphrase: bytes, salt: bytes, *, n: int = 2**14, r: int = 8, p: int = 1) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p)
    return kdf.derive(passphrase)


def _get_chunk_id_from_path(p: str) -> str:
    m = re.search(r"part-(\d+)\.parquet$", p)
    return m.group(1) if m else p


def _list_chunk_paths(zf: ZipFile) -> List[str]:
    return [n for n in zf.namelist() if n.startswith("chunks/") and n.endswith(".parquet")]


def _read_parquet_from_zip(zf: ZipFile, name: str) -> pd.DataFrame:
    with zf.open(name, "r") as f:
        buf = io.BytesIO(f.read())
    return pq.read_table(buf).to_pandas()


def _write_parquet_to_bytes(df: pd.DataFrame) -> bytes:
    table = pa.Table.from_pandas(df, preserve_index=False)
    out = io.BytesIO()
    pq.write_table(table, out)
    return out.getvalue()


def _rewrite_zip_with_replacements(
    src_path: str,
    *,
    replacements: Dict[str, bytes],
    additions: Dict[str, bytes],
) -> None:
    """Reescribe el .surx de forma atómica, creando el tmp en la MISMA carpeta
    que el destino y evitando duplicados (no copiamos nombres que luego agregamos)."""
    dst_dir = os.path.dirname(os.path.abspath(src_path)) or "."
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".surx.tmp", dir=dst_dir)
    os.close(tmp_fd)
    try:
        with ZipFile(src_path, "r") as zsrc, ZipFile(tmp_path, "w", compression=ZIP_DEFLATED) as zdst:
            skip_names = set(replacements.keys()) | set(additions.keys())
            for name in zsrc.namelist():
                if name in skip_names:
                    continue  # no copiar, se escribirá nuevo
                zdst.writestr(name, zsrc.read(name))
            # Escribir reemplazos + adiciones
            for name, data in {**replacements, **additions}.items():
                zdst.writestr(name, data)
        os.replace(tmp_path, src_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# -------------------- API principal --------------------

def encrypt_columns_in_surx(path: str, cols: Iterable[str], passphrase: str) -> None:
    cols = list(dict.fromkeys([c.strip() for c in cols if c and c.strip()]))
    if not cols:
        raise ValueError("No se especificaron columnas a cifrar")

    salt = os.urandom(SALT_SIZE)
    key = _derive_key(passphrase.encode("utf-8"), salt)
    aes = AESGCM(key)

    with ZipFile(path, "r") as zf:
        chunk_paths = _list_chunk_paths(zf)
        parts: Dict[str, List[str]] = {}
        additions: Dict[str, bytes] = {}
        replacements: Dict[str, bytes] = {}

        for cp in chunk_paths:
            part_id = _get_chunk_id_from_path(cp)
            df = _read_parquet_from_zip(zf, cp)
            present_cols = [c for c in cols if c in df.columns]
            if not present_cols:
                continue

            # Cifrar y guardar side-cars
            for col in present_cols:
                col_df = pd.DataFrame({col: df[col]})
                plain = _write_parquet_to_bytes(col_df)
                nonce = os.urandom(NONCE_SIZE)
                ad = f"part:{part_id}|col:{col}".encode()
                ct = aes.encrypt(nonce, plain, associated_data=ad)
                blob = nonce + ct  # nonce || ciphertext+tag
                additions[f"{ENC_DIR}/part-{part_id}/{col}.bin"] = blob
                parts.setdefault(part_id, []).append(col)

            # Reescribir chunk sin las columnas cifradas
            df_drop = df.drop(columns=present_cols)
            replacements[cp] = _write_parquet_to_bytes(df_drop)

        # -------------------- (fix) evitar re-cifrar vacío que rompe parts --------------------
        encrypted_cols = sorted({c for clist in parts.values() for c in clist})
        if not encrypted_cols:
            # nada para cifrar (ya estaban removidas de los chunks)
            raise ValueError("Ninguna de las columnas especificadas estaba en texto plano para cifrar.")
        # --------------------------------------------------------------------------------------

        # Guardar metadatos
        meta = CryptoMeta(
            algo="AESGCM",
            kdf="scrypt",
            scrypt_n=2**14,
            scrypt_r=8,
            scrypt_p=1,
            salt_hex=salt.hex(),
            columns=encrypted_cols,  # usa las realmente cifradas
            parts=parts,
        )
        additions[CRYPTO_CONFIG_PATH] = json.dumps(meta.to_dict(), ensure_ascii=False, indent=2).encode("utf-8")

    _rewrite_zip_with_replacements(path, replacements=replacements, additions=additions)


def load_crypto_meta(zf: ZipFile) -> CryptoMeta | None:
    if CRYPTO_CONFIG_PATH not in zf.namelist():
        return None
    data = json.loads(zf.read(CRYPTO_CONFIG_PATH))
    s = data.get("scrypt", {})
    return CryptoMeta(
        algo=data.get("algo", "AESGCM"),
        kdf=data.get("kdf", "scrypt"),
        scrypt_n=int(s.get("n", 2**14)),
        scrypt_r=int(s.get("r", 8)),
        scrypt_p=int(s.get("p", 1)),
        salt_hex=str(s.get("salt")),
        columns=list(data.get("columns", [])),
        parts={k: list(v) for k, v in (data.get("parts", {}) or {}).items()},
    )


def rehydrate_chunk_columns(
    zf: ZipFile,
    df_chunk: pd.DataFrame,
    chunk_path: str,
    *,
    passphrase: str,
    want_cols: Iterable[str] | None,
) -> pd.DataFrame:
    meta = load_crypto_meta(zf)
    if not meta:
        return df_chunk

    from cryptography.exceptions import InvalidTag

    salt = bytes.fromhex(meta.salt_hex)
    key = _derive_key(passphrase.encode("utf-8"), salt, n=meta.scrypt_n, r=meta.scrypt_r, p=meta.scrypt_p)
    aes = AESGCM(key)

    part_id = _get_chunk_id_from_path(chunk_path)

    # Descubrir columnas disponibles por side-cars (ignora meta.parts vacío)
    want = set(want_cols or meta.columns)
    cols_here = {c for c in want if f"enc/part-{part_id}/{c}.bin" in zf.namelist()}
    if not cols_here:
        return df_chunk

    out = df_chunk.copy()
    for col in cols_here:
        enc_name = f"enc/part-{part_id}/{col}.bin"
        blob = zf.read(enc_name)
        nonce, ct = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
        try:
            plain = aes.decrypt(nonce, ct, associated_data=f"part:{part_id}|col:{col}".encode())
        except InvalidTag:
            raise ValueError("Passphrase incorrecta o datos cifrados corruptos")  # error claro
        col_df = pq.read_table(io.BytesIO(plain)).to_pandas()
        if col not in col_df.columns or len(col_df) != len(out):
            raise ValueError(f"Side-car inválido para {col}")
        out[col] = col_df[col].values
    return out
