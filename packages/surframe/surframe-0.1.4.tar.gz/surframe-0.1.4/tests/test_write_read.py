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
import pandas as pd
from zipfile import ZipFile

from surframe import write, read, inspect

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
OUT = EXAMPLES / "sales.surx"
SCHEMA = EXAMPLES / "sales.schema.json"
CSV = EXAMPLES / "sales.csv"

def test_convert_and_read_pruned(tmp_path):
    # Copiar ejemplos a tmp para no pisar el repo
    tmp_csv = tmp_path / "sales.csv"
    tmp_csv.write_text(CSV.read_text(encoding="utf-8"), encoding="utf-8")
    tmp_schema = tmp_path / "sales.schema.json"
    tmp_schema.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    tmp_out = tmp_path / "sales.surx"

    # Escribir
    schema = json.loads(tmp_schema.read_text(encoding="utf-8"))
    write(str(tmp_csv), str(tmp_out), schema=schema)

    assert tmp_out.exists()

    # Leer con filtro (solo AR y ts >= 2025-01-01)
    df = read(str(tmp_out), columns=["ts", "country", "price"], where="country=='AR' and ts>='2025-01-01'")
    assert not df.empty
    assert set(df["country"]) == {"AR"}
    assert pd.to_datetime(df["ts"], utc=True).min() >= pd.Timestamp("2025-01-01", tz="UTC")

    # Inspect debe listar índices y chunks
    info = inspect(str(tmp_out))
    assert info["n_chunks"] >= 1
    assert any(n.endswith("ts.minmax.json") for n in info["indexes"])
    assert any(n.endswith("country.bloom.json") for n in info["indexes"])

def test_container_layout(tmp_path):
    # escribir contenedor
    tmp_out = tmp_path / "sales.surx"
    write(str(CSV), str(tmp_out))
    with ZipFile(tmp_out, "r") as zf:
        names = zf.namelist()
        assert "manifest.json" in names
        assert any(n.startswith("chunks/") and n.endswith(".parquet") for n in names)
        assert "indexes/ts.minmax.json" in names
        assert "indexes/country.bloom.json" in names
