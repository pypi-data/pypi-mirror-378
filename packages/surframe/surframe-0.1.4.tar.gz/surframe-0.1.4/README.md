# SURFRAME (SUR = Semantic Unified Record)

Formato de datos + toolkit para reemplazar CSV/JSONL con tipado fuerte, Ã­ndices y linaje.

## MVP (paso actual)
- Estructura de repo creada.
- NÃºcleo operativo: `write/read` con particionado por `country`, Ã­ndices `minmax`/`bloom`, `plan`, `inspect`, `validate`, `reindex`, `optimize`, `stats`, `advise`.
- CLI `surx` incluida.

## InstalaciÃ³n (editable)
```bash
pip install -e .
surx --help

Ver guía de uso: [docs/usage.md](docs/usage.md)
