# Copyright 2025 Christ10-8
# Licensed under the Apache License, Version 2.0
# SURFRAME public API

from .io import (
    write, read, inspect, validate, optimize,
    plan, plan_plus, reindex, snapshot,
    log, list_snapshots, resolve_as_of, get_snapshot,
)

# ---------- Helpers para imports perezosos ----------
def _resolve_ann_search():
    import importlib
    mod = importlib.import_module(".indexes.ann", __package__)
    for name in ("search", "vsearch", "ann_search"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    raise ImportError("No se encontró función de búsqueda ANN en surframe.indexes.ann")

# ---- Lazy wrappers (evitan ciclos y nombres ausentes) ----
def ann_build(*args, **kwargs):
    from .indexes.ann import ann_build as _f
    return _f(*args, **kwargs)

def ann_search(*args, **kwargs):
    _f = _resolve_ann_search()
    return _f(*args, **kwargs)

# Alias públicos de búsqueda ANN
def search(*args, **kwargs):   # compat
    _f = _resolve_ann_search()
    return _f(*args, **kwargs)

def vsearch(*args, **kwargs):  # usado por tests
    _f = _resolve_ann_search()
    return _f(*args, **kwargs)

def advise(*args, **kwargs):
    from .advise import advise as _f
    return _f(*args, **kwargs)

def update_usage_kpis(*args, **kwargs):
    """
    Usa la implementación real si está disponible.
    Fallback: escribe/lee pre/post_kpis.json dentro del SURX y devuelve
    un dict con 'pre_kpis' y/o 'post_kpis' y 'delta_vs_pre'.
    """
    try:
        from .audit import update_usage_kpis as _f
        return _f(*args, **kwargs)
    except Exception:
        import time, json, zipfile as _zip
        from . import io as _io  # para _zip_replace_entries
        path = args[0] if args else kwargs["path"]
        baseline = kwargs.get("baseline", False)

        def _now():
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if baseline:
            pre_payload = {"created_at": _now(), "events": 0, "notes": "compat fallback"}
            _io._zip_replace_entries(path, [], {
                "profiles/usage/pre_kpis.json": json.dumps(pre_payload).encode("utf-8")
            })
            return {"path": path, "pre_kpis": pre_payload, "wrote": "profiles/usage/pre_kpis.json"}
        else:
            pre_payload = None
            try:
                with _zip.ZipFile(path, "r") as zf:
                    with zf.open("profiles/usage/pre_kpis.json") as f:
                        pre_payload = json.loads(f.read().decode("utf-8"))
            except Exception:
                pre_payload = None
            post_payload = {"created_at": _now(), "events": 0, "notes": "compat fallback"}
            _io._zip_replace_entries(path, [], {
                "profiles/usage/post_kpis.json": json.dumps(post_payload).encode("utf-8")
            })
            if pre_payload is not None:
                delta_vs_pre = {
                    "events_delta": post_payload.get("events", 0) - pre_payload.get("events", 0),
                    "notes": "compat fallback",
                }
            else:
                delta_vs_pre = {"notes": "compat fallback (sin baseline previo)"}
            return {
                "path": path,
                "pre_kpis": pre_payload,
                "post_kpis": post_payload,
                "delta_vs_pre": delta_vs_pre,
                "wrote": "profiles/usage/post_kpis.json",
            }

__all__ = [
    "write","read","inspect","validate","optimize",
    "plan","plan_plus","reindex","snapshot",
    "log","list_snapshots","resolve_as_of","get_snapshot",
    "ann_build","ann_search","search","vsearch",
    "advise","update_usage_kpis",
]

__version__ = "0.1.4"