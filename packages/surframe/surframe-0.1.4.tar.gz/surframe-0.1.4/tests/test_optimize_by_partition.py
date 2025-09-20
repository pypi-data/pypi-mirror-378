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


import zipfile, re
import pandas as pd
import surframe as sur

def test_optimize_keeps_partitions(tmp_path):
    # dataset con particiones country=AR/CL/UY
    df = pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=900, freq="min"),
        "country": (["AR","CL","UY"]*300),
        "price": range(900),
    })
    p = tmp_path/"sales.surx"
    sur.write(df, str(p), indexes={"country":{"bloom":{}}, "ts":{"minmax":{}}})

    # optimiza y ordena por ts, con chunks pequeños
    out = sur.optimize(str(p), compact=True, target_rows=100, order=["ts"], min_chunks=3)
    assert out["changed"] and out["new_parts"] >= 3

    # verifica que se mantengan los prefijos por partición
    with zipfile.ZipFile(p, "r") as zf:
        chunks = [n for n in zf.namelist() if n.startswith("chunks/") and n.endswith(".parquet")]
        assert any(n.startswith("chunks/country=AR/") for n in chunks)
        assert any(n.startswith("chunks/country=CL/") for n in chunks)
        assert any(n.startswith("chunks/country=UY/") for n in chunks)

    # reindex reconstruido y pruning operativo
    plan = sur.plan(str(p), where="country='AR' and ts>='2025-01-01' and ts<'2025-01-02'")
    assert plan and "candidates" in plan
    assert len(plan["candidates"]) >= 1
