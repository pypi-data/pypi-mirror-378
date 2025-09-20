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

def test_usage_aggregate(tmp_path, monkeypatch):
    # preparar .surx
    root = Path(tmp_path)
    df = None
    # reutilizamos examples si existen; si no, generamos
    import pandas as pd
    df = pd.DataFrame({
        "ts": pd.to_datetime(["2025-01-01","2025-01-02","2025-02-01","2025-01-03","2025-02-10","2025-01-04"]),
        "country": ["AR","AR","AR","CL","CL","UY"],
        "price": [10.5,12.0,11.3,8.7,7.9,9.1],
    })
    out = root / "s.surx"
    schema = {"version":1,"name":"s","schema":[
        {"name":"ts","arrow_type":"timestamp[us, UTC]"},
        {"name":"country","arrow_type":"utf8"},
        {"name":"price","arrow_type":"float64"},
    ], "partitions":[{"by":"country"}]}
    sur.write(df, str(out), schema=schema)
    # disparar algunas lecturas
    sur.read(str(out), columns=["ts","price"], where="country='AR'")
    sur.read(str(out), columns=["ts","country","price"], where="price>10")
    sur.read(str(out), columns=["ts"], where=None)
    info = sur.inspect(str(out))
    agg = info.get("usage_agg")
    assert agg and agg["reads"] >= 3
    assert agg["bytes_total"] > 0
    assert agg["bytes_p50"] >= 0.0
