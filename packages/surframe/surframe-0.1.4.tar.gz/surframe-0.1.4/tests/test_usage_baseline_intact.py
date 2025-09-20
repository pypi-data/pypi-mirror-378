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


import pandas as pd, surframe as sur, json, zipfile

def test_usage_baseline_survives_optimize(tmp_path):
    df = pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=2000, freq="min"),
        "country": ["AR"]*1000 + ["CL"]*1000,
        "price": range(2000),
    })
    p = tmp_path/"u.surx"
    sur.write(df, str(p), indexes={"country":{"bloom":{}}, "ts":{"minmax":{}}})

    # ANTES + baseline
    for _ in range(5):
        sur.read(str(p), where="country='AR' and ts>='2025-01-02' and ts<'2025-01-03'", columns=["ts","country","price"])
    sur.update_usage_kpis(str(p), baseline=True)

    # optimize
    sur.optimize(str(p), compact=True, target_rows=500, order=["ts"], min_chunks=4)

    # DESPUÉS
    for _ in range(5):
        sur.read(str(p), where="country='AR' and ts>='2025-01-02' and ts<'2025-01-03'", columns=["ts","country","price"])
    out = sur.update_usage_kpis(str(p))

    assert out["pre_kpis"] is not None
    assert out["post_kpis"] is not None
    assert out["delta_vs_pre"] is not None
