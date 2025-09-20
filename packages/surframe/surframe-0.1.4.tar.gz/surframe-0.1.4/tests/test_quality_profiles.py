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
import surframe as sur

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
CSV = EXAMPLES / "sales.csv"
SCHEMA = EXAMPLES / "sales.schema.json"

def test_quality_hll_and_percentiles(tmp_path):
    # preparar .surx
    tmp_csv = tmp_path / "sales.csv"
    tmp_csv.write_text(CSV.read_text(encoding="utf-8"), encoding="utf-8")
    tmp_schema = tmp_path / "sales.schema.json"
    tmp_schema.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "sales.surx"
    sur.write(str(tmp_csv), str(out), schema=json.loads(tmp_schema.read_text(encoding="utf-8")))

    # validar (genera perfiles avanzados)
    sur.validate(str(out))

    info = sur.inspect(str(out))
    assert info["rows"] == 6
    q = info["quality"]["columns"]
    # HLL estimado en country ~ 3
    assert abs(q["country"]["distinct_est"] - 3) < 0.5
    # percentiles de price: dataset pequeño conocido
    assert q["price"]["p50"] is not None
    assert q["price"]["p95"] is not None
    assert q["price"]["p99"] is not None
    assert q["price"]["p50"] <= q["price"]["p95"] <= q["price"]["p99"]
