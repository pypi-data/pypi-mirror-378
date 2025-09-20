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
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

import surframe as sur

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
CSV = EXAMPLES / "sales.csv"
SCHEMA = EXAMPLES / "sales.schema.json"


def _fresh_surx(tmp_path: Path) -> Path:
    tmp_csv = tmp_path / "sales.csv"
    tmp_csv.write_text(CSV.read_text(encoding="utf-8"), encoding="utf-8")
    tmp_schema = tmp_path / "sales.schema.json"
    tmp_schema.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "sales.surx"
    sur.write(str(tmp_csv), str(out), schema=json.loads(tmp_schema.read_text(encoding="utf-8")))
    return out


def test_plan_and_reindex_minmax_price(tmp_path):
    out = _fresh_surx(tmp_path)

    # Sin índice de price: plan no puede podar
    plan_noidx = sur.plan(str(out), where="price>10")
    assert plan_noidx["candidates_count"] == plan_noidx["total_chunks"] == 3

    # Construir índice minmax para price
    sur.reindex(str(out), {"price": {"minmax": {}}})

    # Con índice: debe podar a 1 chunk (AR)
    plan_idx = sur.plan(str(out), where="price>10")
    assert plan_idx["candidates_count"] == 1
    assert plan_idx["candidates_final"] == ["000000"]  # chunk AR en este dataset

    # Leer aplicando ese filtro → debe escanear 1 chunk y devolver 3 filas (AR)
    df = sur.read(str(out), columns=["ts", "country", "price"], where="price>10")
    assert len(df) == 3
    assert set(df["country"]) == {"AR"}

    # Confirmar métricas de lectura desde inspect (último uso)
    info = sur.inspect(str(out))
    last = info["last_usage"]
    assert last["chunks_scanned"] == 1
    assert last["bytes_read"] > 0
