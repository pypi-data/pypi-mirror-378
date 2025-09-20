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
import surframe as sur

def test_optimize_and_reindex(tmp_path):
    import pandas as pd
    df = pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=3000, freq="h"),
        "country": ["AR","CL","UY"] * 1000,
        "price": list(range(3000)),
    })
    path = tmp_path / "sales.surx"
    sur.write(df, str(path), indexes={"country": {"bloom": {}}, "ts": {"minmax": {}}})

    out = sur.optimize(str(path), compact=True, target_rows=500, order=["ts"])
    assert out["changed"] and out["new_parts"] > 1
    assert set(out["reindexed_columns"]) >= {"country", "ts"}

def test_advise_runs(tmp_path):
    import pandas as pd
    df = pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=100, freq="h"),
        "country": ["AR","CL","UY","AR"] * 25,
        "price": list(range(100)),
    })
    path = tmp_path / "demo.surx"
    sur.write(df, str(path), indexes={"country": {"bloom": {}}, "ts": {"minmax": {}}})
    # Generar eventos de uso
    for _ in range(5):
        _ = sur.read(str(path), where="country='AR' and ts>='2025-01-02'", columns=["ts","country"])
    recs = sur.advise(str(path))
    assert isinstance(recs, dict) and "recommendations" in recs

def test_plan_plus(tmp_path):
    import pandas as pd
    df = pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=48, freq="h"),
        "country": ["AR","CL","UY","AR"] * 12,
        "price": list(range(48)),
    })
    path = tmp_path / "p.surx"
    sur.write(df, str(path), indexes={"country": {"bloom": {}}, "ts": {"minmax": {}}})
    res = sur.plan_plus(str(path), "country IN ('AR','CL') AND ts BETWEEN '2025-01-01' AND '2025-01-03'")
    assert res["count"] >= 1 and isinstance(res["candidates"], list)
