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
import json
import os
import getpass
from typing import Optional, List
from zipfile import ZipFile

import typer
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import surframe as sur
from surframe.io import encrypt as encrypt_io  # nuevo: CLI de cifrado
from surframe.crypto import load_crypto_meta, _derive_key

app = typer.Typer(no_args_is_help=True)
os.environ.setdefault("SURX_CLIENT", "cli")


def _parse_indexes(index: Optional[str]) -> dict:
    """
    Convierte "--index 'country:bloom,ts:minmax,price:minmax'" a
    {"country":{"bloom":{}}, "ts":{"minmax":{}}, "price":{"minmax":{}}}
    """
    if not index:
        return {}
    out = {}
    parts = [p.strip() for p in index.split(",") if p.strip()]
    for p in parts:
        if ":" not in p:
            raise typer.BadParameter(f"Índice inválido: {p}")
        col, kind = p.split(":", 1)
        out.setdefault(col, {})[kind] = {}
    return out


def _normalize_as_of(path: str, as_of: Optional[str]) -> Optional[str]:
    """
    Normaliza tokens de --as-of:
      - latest
      - snapshots/<archivo>.json (acepta '\\' en Windows)
      - ISO8601
    """
    if not as_of:
        return None
    token = as_of.replace("\\", "/")  # tolerar backslashes en Windows
    resolved = sur.resolve_as_of(path, token)
    return resolved or token


@app.command()
def write(
    source: str = typer.Argument(..., help="CSV/Parquet de entrada"),
    out: str = typer.Option(..., "--out", "-o", help="Salida .surx"),
    schema: Optional[str] = typer.Option(None, "--schema", help="Manifest/schema JSON"),
    index: Optional[str] = typer.Option(None, "--index", help='Ej: "country:bloom,ts:minmax"'),
):
    """Escribe un SURX desde CSV/Parquet con índices básicos."""
    schema_obj = json.loads(open(schema, "r", encoding="utf-8").read()) if schema else None
    idx = _parse_indexes(index)
    sur.write(source, out, schema=schema_obj, indexes=idx)
    typer.echo(f"[ok] Escrito {out}")


@app.command()
def read(
    path: str = typer.Argument(..., help="Ruta .surx"),
    columns: Optional[str] = typer.Option(None, "--cols", "--columns", help="Columnas separadas por coma"),
    where: Optional[str] = typer.Option(None, "--where", help="Filtro simple (AND)"),
    head: Optional[int] = typer.Option(None, "--head", help="Mostrar primeras N filas"),
    to_csv: Optional[str] = typer.Option(None, "--to-csv", help="Guardar salida a CSV"),
    explain: bool = typer.Option(False, "--explain", help="Imprime plan de pruning y sale"),
    as_of: Optional[str] = typer.Option(None, "--as-of", help="ISO | latest | snapshots/<file>.json"),
    passfile: Optional[str] = typer.Option(None, "--passfile", help="Archivo con la passphrase (opcional)"),
    ask_pass: bool = typer.Option(False, "--ask-pass", help="Pedir pass por consola"),
    use_env_pass: bool = typer.Option(False, "--use-env-pass", help="Tomar pass desde SURX_PASS explícitamente"),
):
    """Lee SURX con proyección y filtro (predicate pruning)."""
    cols = [c.strip() for c in columns.split(",")] if columns else None
    as_of_norm = _normalize_as_of(path, as_of)

    if explain:
        plan_info = sur.plan(path, where=where, as_of=as_of_norm)
        typer.echo(json.dumps(plan_info, ensure_ascii=False, indent=2))
        raise typer.Exit(0)

    # Prioridad: passfile > --ask-pass > --use-env-pass
    passphrase: Optional[str] = None
    if passfile:
        with open(passfile, "rb") as f:
            raw = f.read()
        for enc in ("utf-8-sig", "utf-16", "latin-1"):
            try:
                passphrase = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if passphrase is not None:
            passphrase = passphrase.replace("\ufeff", "").strip().strip('"').strip("'")
    elif ask_pass:
        passphrase = getpass.getpass("Passphrase: ").strip()
    elif use_env_pass:
        env = os.environ.get("SURX_PASS") or ""
        env = env.replace("\ufeff", "").strip().strip('"').strip("'")
        passphrase = env or None

    # Nota: sur.read debe soportar passphrase para rehidratar columnas cifradas
    try:
        df = sur.read(path, columns=cols, where=where, as_of=as_of_norm, passphrase=passphrase)
    except ValueError as e:
        msg = str(e)
        if use_env_pass and "Passphrase incorrecta" in msg:
            typer.secho(
                "La pass de SURX_PASS no coincide con la usada al cifrar. "
                "Probá con --ask-pass o re-cifrando con --use-env-pass.",
                fg=typer.colors.RED,
            )
        raise

    if to_csv:
        df.to_csv(to_csv, index=False)
        typer.echo(f"[ok] Guardado CSV en {to_csv} ({len(df)} filas)")
    else:
        if head:
            df = df.head(head)
        typer.echo(df.to_string(index=False))


# --- plan (PLUS autodetección) ---------------------------------------------
@app.command(help="Muestra plan de poda; soporta OR/IN/BETWEEN (PLUS)")
def plan(
    path: str = typer.Argument(..., help="Ruta al .surx"),
    where: Optional[str] = typer.Option(None, "--where", help="Expresión de filtro"),
    as_of: Optional[str] = typer.Option(None, "--as-of", help="ISO | latest | snapshots/<file>.json"),
    plus: bool = typer.Option(True, "--plus/--no-plus", help="Usar Planner PLUS si aplica"),
):
    if not where:
        typer.secho("--where es requerido", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    as_of_norm = _normalize_as_of(path, as_of)
    import re as _re

    # Si el filtro contiene OR/IN/BETWEEN y existe plan_plus, usarlo
    if plus and _re.search(r"(?i)\bOR\b|\bIN\b|\bBETWEEN\b", where) and hasattr(sur, "plan_plus"):
        res = sur.plan_plus(path, where)
    else:
        res = sur.plan(path, where=where, as_of=as_of_norm)
    typer.echo(json.dumps(res, ensure_ascii=False, indent=2))


@app.command()
def inspect(
    path: str = typer.Argument(..., help="Ruta .surx"),
    json_out: bool = typer.Option(False, "--json", help="Imprime el JSON completo de inspect()"),
):
    """Muestra resumen del dataset, índices y calidad (si disponible)."""
    info = sur.inspect(path)
    if json_out:
        typer.echo(json.dumps(info, ensure_ascii=False, indent=2))
        raise typer.Exit(0)

    typer.echo(f"Dataset: {info['name']}")
    typer.echo(f"Creado:  {info.get('created_at')}")
    if info.get("rows") is not None:
        typer.echo(f"Filas:   {info['rows']}")
    typer.echo(f"Chunks:  {info['n_chunks']}  |  Tamaño (zip): {info['bytes_total']} bytes")
    typer.echo(f"Particiones: {info['partitions']}")
    typer.echo(f"Índices:     {info['indexes']}")

    q = info.get("quality") or {}
    qc = (q.get("columns") or {})
    if qc:
        parts = []
        if "ts" in qc:
            parts.append(
                f"ts[min,max]=[{qc['ts'].get('min')}, {qc['ts'].get('max')}] "
                f"null%={qc['ts'].get('null_pct'):.3f}"
            )
        if "country" in qc:
            de = qc["country"].get("distinct_est")
            parts.append(
                f"country[distinct_est]≈{int(de) if de is not None else 'NA'} "
                f"null%={qc['country'].get('null_pct'):.3f}"
            )
        if "price" in qc:
            p50 = qc["price"].get("p50"); p95 = qc["price"].get("p95"); p99 = qc["price"].get("p99")
            if p50 is not None:
                parts.append(f"price[p50/p95/p99]={p50:.3f}/{p95:.3f}/{p99:.3f}")
        if parts:
            typer.echo("Calidad:  " + " ".join(["|"] + parts) if parts else "")

    last = info.get("last_usage")
    if last:
        typer.echo("Última lectura:")
        typer.echo(f"  where='{last.get('where')}', cols={last.get('columns')}")
        typer.echo(f"  bytes_read={last.get('bytes_read')}, chunks_scanned={last.get('chunks_scanned')}")

    agg = info.get("usage_agg")
    if agg:
        typer.echo("Uso agregado (últimas lecturas):")
        typer.echo(f"  reads={agg.get('reads')}, bytes_total={agg.get('bytes_total')}, chunks_total={agg.get('chunks_total')}")
        typer.echo(f"  bytes p50/p95={agg.get('bytes_p50'):.0f}/{agg.get('bytes_p95'):.0f}  |  chunks p50/p95={agg.get('chunks_p50'):.2f}/{agg.get('chunks_p95'):.2f}")
        top_cols = ", ".join([f"{k}({v})" for k, v in (agg.get('top_columns') or [])])
        if top_cols:
            typer.echo(f"  top_columns: {top_cols}")
        top_where = ", ".join([f"{k}({v})" for k, v in (agg.get('top_where') or [])])
        if top_where:
            typer.echo(f"  top_where: {top_where}")

    snaps = info.get("snapshots") or {}
    if snaps:
        typer.echo(f"Snapshots: count={snaps.get('count')} last_ts={snaps.get('last_ts')}")
    journal = info.get("journal") or {}
    if journal:
        typer.echo(f"Journal:   count={journal.get('count')}")


@app.command()
def validate(path: str = typer.Argument(..., help="Ruta .surx")):
    """Valida constraints del manifest y actualiza profiles/quality.json."""
    sur.validate(path)
    typer.echo("[ok] Validación completada y quality.json actualizado")


# --- optimize (Nivel 4) ----------------------------------------------------
@app.command(help="Recomponer chunks (compactar/ordenar) y reindexar afectado.")
def optimize(
    path: str = typer.Argument(..., help="Ruta al .surx"),
    compact: bool = typer.Option(False, "--compact", help="Compacta chunks a un tamaño objetivo"),
    target_rows: int = typer.Option(100_000, "--target-rows", help="Filas objetivo por chunk"),
    order: Optional[str] = typer.Option(None, "--order", help="Columnas de orden (coma-sep)"),
    min_chunks: int = typer.Option(1, "--min-chunks", help="Mínimo de chunks tras optimizar"),
):
    order_cols = [c.strip() for c in order.split(",")] if order else None
    try:
        res = sur.optimize(
            path,
            compact=compact,
            target_rows=target_rows,
            order=order_cols,
            min_chunks=min_chunks,
        )
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=2)

    # --- Mensaje friendly opcional cuando --order ts y --compact ---
    if compact and order_cols and order_cols == ["ts"]:
        # Extraer info útil de la respuesta si existe; caer con defaults si no.
        reindexed = res.get("reindexed") if isinstance(res, dict) else None
        if isinstance(reindexed, dict):
            recon = ", ".join(
                f"{kind}({', '.join(cols)})" for kind, cols in reindexed.items() if cols
            ) or "ninguno"
        else:
            recon = "desconocido"

        n_chunks_total = (
            (res.get("n_chunks_after") if isinstance(res, dict) else None)
            or (res.get("chunks_after") if isinstance(res, dict) else None)
            or (res.get("n_chunks") if isinstance(res, dict) else None)
            or 0
        )
        n_parts = (
            (res.get("n_partitions_after") if isinstance(res, dict) else None)
            or (res.get("n_partitions") if isinstance(res, dict) else None)
        )
        if n_parts and n_chunks_total:
            approx_per_part = max(1, int(round(n_chunks_total / n_parts)))
            msg = f"Reescritos ≈{approx_per_part} chunks por partición, ordenados por ts. Reconstruidos: {recon}."
        else:
            msg = f"Reescritos {n_chunks_total} chunks, ordenados por ts. Reconstruidos: {recon}."
        typer.secho(msg, fg=typer.colors.GREEN)

    # Siempre imprimimos también el JSON con el resultado completo
    typer.echo(json.dumps(res, ensure_ascii=False, indent=2))


# --- stats (KPIs de uso post/pre) ------------------------------------------
@app.command(help="Calcula y guarda KPIs agregados de uso. Baseline: pre_kpis; Post: post_kpis + delta.")
def stats(
    path: str = typer.Argument(..., help="Ruta al .surx"),
    window: Optional[int] = typer.Option(None, "--window", help="Usar los últimos N eventos"),
    baseline: bool = typer.Option(False, "--baseline/--no-baseline", help="Guardar baseline (pre_kpis) en lugar de post"),
):
    res = sur.update_usage_kpis(path, window=window, baseline=baseline)
    typer.echo(json.dumps(res, ensure_ascii=False, indent=2))


@app.command()
def reindex(
    path: str = typer.Argument(..., help="Ruta .surx"),
    index: Optional[str] = typer.Option(None, "--index", help='Ej: "price:minmax" o "country:bloom"'),
):
    """Reconstruye índices (post-hoc)."""
    if not index:
        raise typer.BadParameter('Debes especificar --index, ej: "price:minmax"')
    idx = _parse_indexes(index)
    sur.reindex(path, idx)
    typer.echo(f"[ok] Reindex aplicado sobre {path}: {index}")


@app.command()
def plan_only(
    path: str = typer.Argument(..., help="Ruta .surx"),
    where: Optional[str] = typer.Option(None, "--where", help="Filtro simple (AND)"),
    as_of: Optional[str] = typer.Option(None, "--as-of", help="ISO | latest | snapshots/<file>.json"),
):
    """Alias histórico, usar `surx plan`."""
    as_of_norm = _normalize_as_of(path, as_of)
    info = sur.plan(path, where=where, as_of=as_of_norm)
    typer.echo(json.dumps(info, ensure_ascii=False, indent=2))


@app.command()
def snapshot(
    path: str = typer.Argument(..., help="Ruta .surx"),
    note: Optional[str] = typer.Option(None, "--note", help="Nota opcional en snapshot"),
):
    """Crea un snapshot del estado actual (chunks, índices, perfiles)."""
    s = sur.snapshot(path, note=note)
    typer.echo(json.dumps(s, ensure_ascii=False, indent=2))


@app.command()
def log(
    path: str = typer.Argument(..., help="Ruta .surx"),
):
    """Lista el journal de eventos."""
    events = sur.log(path)
    typer.echo(json.dumps(events, ensure_ascii=False, indent=2))


@app.command()
def snapshots(path: str = typer.Argument(..., help="Ruta .surx")):
    """Lista todos los snapshots disponibles en el contenedor."""
    items = sur.list_snapshots(path)
    typer.echo(json.dumps(items, ensure_ascii=False, indent=2))


@app.command()
def checkout(
    path: str = typer.Argument(..., help="Ruta .surx"),
    as_of: Optional[str] = typer.Option(None, "--as-of", help="ISO | latest | snapshots/<file>.json"),
):
    """
    Muestra el snapshot exacto que se usará (chunks/indexes) para una lectura histórica.
    """
    as_of_norm = _normalize_as_of(path, as_of)
    snap = sur.get_snapshot(path, as_of=as_of_norm)
    typer.echo(json.dumps(snap, ensure_ascii=False, indent=2))


@app.command()
def encrypt(
    path: str = typer.Argument(..., help="Ruta al .surx"),
    cols: str = typer.Option(..., "--cols", help="Columnas a cifrar (coma-sep)"),
    passfile: Optional[str] = typer.Option(None, "--passfile", help="Archivo con la passphrase"),
    ask_pass: bool = typer.Option(False, "--ask-pass", help="Pedir pass por consola"),
    use_env_pass: bool = typer.Option(False, "--use-env-pass", help="Tomar pass desde SURX_PASS explícitamente"),
):
    """
    Cifra columnas sensibles con AES-GCM (side-cars). No cifres columnas que usen índices.
    """
    columns = [c.strip() for c in cols.split(",") if c.strip()]

    # Prioridad: passfile > --ask-pass > --use-env-pass
    passphrase: Optional[str] = None
    if passfile:
        with open(passfile, "rb") as f:
            raw = f.read()
        for enc in ("utf-8-sig", "utf-16", "latin-1"):
            try:
                passphrase = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        passphrase = (passphrase or "").replace("\ufeff", "").strip().strip('"').strip("'")
    elif ask_pass:
        passphrase = getpass.getpass("Passphrase: ").strip()
    elif use_env_pass:
        env = os.environ.get("SURX_PASS") or ""
        passphrase = env.replace("\ufeff", "").strip().strip('"').strip("'") or None

    if not passphrase:
        raise typer.BadParameter("Falta passphrase (usa --passfile, --ask-pass o --use-env-pass).")

    encrypt_io(path, columns, passphrase)
    typer.secho("✔ Columnas cifradas y chunks reescritos (side-cars creados).", fg=typer.colors.GREEN)


@app.command()
def crypto_check(
    path: str = typer.Argument(..., help="Ruta al .surx"),
    passfile: Optional[str] = typer.Option(None, "--passfile", help="Archivo con la passphrase"),
    ask_pass: bool = typer.Option(False, "--ask-pass", help="Pedir pass por consola"),
    use_env_pass: bool = typer.Option(False, "--use-env-pass", help="Tomar pass de SURX_PASS"),
):
    """
    Verifica si una passphrase es válida para el cifrado de este SURX sin necesidad de leer datos.
    Retornos:
      - código 0: pass válida
      - código 1: pass inválida o datos corruptos
      - código 2: el SURX no posee metadatos/side-cars de cifrado
    """
    # Obtener passphrase (mismo patrón que read/encrypt)
    passphrase: Optional[str] = None
    if passfile:
        with open(passfile, "rb") as f:
            raw = f.read()
        for enc in ("utf-8-sig", "utf-16", "latin-1"):
            try:
                passphrase = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        passphrase = (passphrase or "").replace("\ufeff", "").strip().strip('"').strip("'")
    elif ask_pass:
        passphrase = getpass.getpass("Passphrase: ").strip()
    elif use_env_pass:
        env = os.environ.get("SURX_PASS") or ""
        passphrase = env.replace("\ufeff", "").strip().strip('"').strip("'") or None

    if not passphrase:
        raise typer.BadParameter("Falta passphrase (usa --passfile, --ask-pass o --use-env-pass).")

    with ZipFile(path, "r") as zf:
        meta = load_crypto_meta(zf)
        if not meta or not meta.columns:
            typer.secho("Este SURX no tiene metadatos de cifrado.", fg=typer.colors.YELLOW)
            raise typer.Exit(code=2)

        # Tomamos cualquier part y columna presentes
        part_id: Optional[str] = None
        col: Optional[str] = None
        if meta.parts:
            part_id = sorted(meta.parts.keys())[0]
            col = meta.parts[part_id][0]
        else:
            # fallback: inferir desde nombres en el zip
            names = zf.namelist()
            cand = [n for n in names if n.startswith("enc/part-") and n.endswith(".bin")]
            if not cand:
                typer.secho("No se encontraron side-cars de cifrado.", fg=typer.colors.YELLOW)
                raise typer.Exit(code=2)
            first = cand[0]  # ej: enc/part-000000/dni.bin
            part_id = first.split("/")[1].split("-")[1]
            col = first.split("/")[-1].replace(".bin", "")

        key = _derive_key(passphrase.encode("utf-8"), bytes.fromhex(meta.salt_hex))
        aes = AESGCM(key)
        blob = zf.read(f"enc/part-{part_id}/{col}.bin")
        nonce, ct = blob[:12], blob[12:]
        try:
            aes.decrypt(nonce, ct, associated_data=f"part:{part_id}|col:{col}".encode("utf-8"))
            typer.secho("✔ Passphrase válida para este SURX.", fg=typer.colors.GREEN)
        except Exception:
            typer.secho("✖ Passphrase inválida o datos corruptos.", fg=typer.colors.RED)
            raise typer.Exit(code=1)


# --------------------------
# ANN (Nivel 2 – índice flat)
# --------------------------

@app.command("ann-build")
def ann_build_cmd(
    path: str = typer.Argument(..., help="Dataset .surx"),
    col: str = typer.Option("embedding", "--col", help="Nombre de la columna vector"),
    metric: str = typer.Option("cosine", "--metric", help="cosine|l2"),
    dim: int = typer.Option(None, "--dim", help="Dimensión (si no, se infiere)"),
):
    """Construye un índice ANN plano (flat) para una columna de embeddings."""
    meta = sur.ann_build(path, col=col, metric=metric, dim=dim)
    typer.echo(f"✔ Índice flat creado: {meta['vectors_n']} vectores, D={meta['dim']}, metric={meta['metric']}")
    typer.echo(f"  -> {meta['vectors_path']}  |  {meta['mapping_path']}")


@app.command("search")
def search_cmd(
    path: str = typer.Argument(..., help="Dataset .surx"),
    q: str = typer.Option(..., "--q", help="Vector coma-sep, ej: 0.1,0.2,0.3"),
    k: int = typer.Option(5, "--topk", help="Top-K"),
    cols: str = typer.Option("", "--cols", help="Columnas a retornar (coma-sep)"),
    where: Optional[str] = typer.Option(None, "--where", help="Filtro opcional (SQL-like simple)"),
    as_of: Optional[str] = typer.Option(None, "--as-of", help="latest | ISO | snapshots/<file>.json"),
    to_csv: Optional[str] = typer.Option(None, "--to-csv", help="Guardar resultado a CSV"),
):
    """Búsqueda vectorial Top-K contra el índice ANN plano."""
    vec = [float(x) for x in q.split(",") if x.strip()]
    columns = [c.strip() for c in cols.split(",") if c.strip()] if cols else None
    as_of_norm = _normalize_as_of(path, as_of) if as_of else None
    df = sur.vsearch(path, query_vec=vec, k=k, where=where, columns=columns, as_of=as_of_norm)
    if to_csv:
        df.to_csv(to_csv, index=False)
        typer.echo(f"[ok] Guardado CSV en {to_csv} ({len(df)} filas)")
    else:
        if len(df) == 0:
            typer.echo("(sin resultados)")
        else:
            typer.echo(df.to_string(index=False))


# --- advise ----------------------------------------------------------------
@app.command(help="Analiza uso/calidad para recomendar índices/particiones/orden")
def advise(
    path: str = typer.Argument(..., help="Ruta al .surx"),
):
    res = sur.advise(path)
    idx = res["recommendations"]["indexes"]
    parts = res["recommendations"]["partitions"]
    order = res["recommendations"]["order"]
    typer.echo("# Recomendaciones\n")
    if idx.get("bloom"):
        typer.echo(f"* Bloom: {', '.join(idx['bloom'])}")
    if idx.get("minmax"):
        typer.echo(f"* MinMax: {', '.join(idx['minmax'])}")
    if parts:
        typer.echo("* Particiones:")
        for p in parts:
            typer.echo(f"  - {p['column']} (distinct_est={p['distinct_est']})")
    if order:
        typer.echo(f"* Orden sugerido: {order}")
    if res.get("estimated_savings"):
        typer.echo(f"* Ahorro estimado: {json.dumps(res['estimated_savings'])}")
    typer.echo("\n## JSON\n" + json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
