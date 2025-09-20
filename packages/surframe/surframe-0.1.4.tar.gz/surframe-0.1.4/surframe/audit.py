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


# surframe/audit.py
from __future__ import annotations
import datetime as _dt
import getpass as _getpass
import hashlib as _hashlib
import json as _json
import os as _os
from typing import Any, Dict, Optional
from zipfile import ZipFile

# Reutilizamos el helper de escritura atómica del cifrado
from .crypto import _rewrite_zip_with_replacements  # ya existe

def _iso_utc() -> str:
    return _dt.datetime.utcnow().replace(tzinfo=_dt.timezone.utc).isoformat().replace("+00:00", "Z")

def _whoami() -> str:
    try:
        return _os.environ.get("SURX_USER") or _getpass.getuser() or "unknown"
    except Exception:
        return "unknown"

def append_audit_event(path: str, event: Dict[str, Any], sign: Optional[bool] = None) -> None:
    """
    Agrega (o crea) una línea JSONL en profiles/audit/YYYYMMDD.jsonl dentro del .surx.
    Control por env:
      - SURX_AUDIT=0   → desactiva (default: activo)
      - SURX_AUDIT_SIGN=1 → firma encadenada por sha256(prev_line)
      - SURX_CLIENT=cli|py → etiqueta de cliente
      - SURX_USER=...  → usuario (fallback: getpass.getuser())
    """
    if str(_os.environ.get("SURX_AUDIT", "1")).lower() in ("0", "false", "no"):
        return

    # Completar defaults seguros
    evt = dict(event)
    evt.setdefault("ts", _iso_utc())
    evt.setdefault("op", "read")
    evt.setdefault("user", _whoami())
    client = _os.environ.get("SURX_CLIENT")
    if client:
        evt.setdefault("client", client)

    # Archivo del día
    date_yyyymmdd = evt["ts"][:10].replace("-", "")
    rel_log = f"profiles/audit/{date_yyyymmdd}.jsonl"

    # Cargar contenido previo (si existe)
    existing: Optional[bytes] = None
    try:
        with ZipFile(path, "r") as zf:
            if rel_log in zf.namelist():
                existing = zf.read(rel_log)
    except FileNotFoundError:
        # dataset no existe (nada que auditar)
        return

    # Firma encadenada opcional
    do_sign = bool(sign) if sign is not None else str(_os.environ.get("SURX_AUDIT_SIGN", "0")).lower() in ("1", "true", "yes")
    if do_sign:
        prev_hash = "0" * 64
        if existing:
            lines = [ln for ln in existing.split(b"\n") if ln.strip()]
            if lines:
                prev_hash = _hashlib.sha256(lines[-1]).hexdigest()

        base = dict(evt)
        # La firma cubre el evento SIN el propio 'sha256', pero SÍ incluye 'prev_sha256'
        base["prev_sha256"] = prev_hash
        payload = _json.dumps(base, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        evt["prev_sha256"] = prev_hash
        evt["sha256"] = _hashlib.sha256(payload).hexdigest()

    # Construir nueva versión del archivo (append)
    line = _json.dumps(evt, ensure_ascii=False) + "\n"
    new_bytes = (existing or b"") + line.encode("utf-8")

    if existing is None:
        _rewrite_zip_with_replacements(path, replacements={}, additions={rel_log: new_bytes})
    else:
        _rewrite_zip_with_replacements(path, replacements={rel_log: new_bytes}, additions={})
