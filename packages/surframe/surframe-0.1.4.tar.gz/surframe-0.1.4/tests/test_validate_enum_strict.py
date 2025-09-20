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
import pytest
from pathlib import Path
import pandas as pd
import surframe as sur

def test_validate_enum_strict(tmp_path):
    df = pd.DataFrame({
        "ts": pd.to_datetime(["2025-01-01","2025-01-02"]),
        "country": ["AR","ZZ"],   # ZZ fuera de enum
        "price": [1.0, 2.0],
    })
    out = tmp_path / "d.surx"
    schema = {
        "version": 1,
        "name": "d",
        "schema": [
            {"name":"ts","arrow_type":"timestamp[us, UTC]","constraints":{"not_null":True}},
            {"name":"country","arrow_type":"utf8","constraints":{"enum":["AR","CL","UY"]}},
            {"name":"price","arrow_type":"float64","constraints":{"min":0}}
        ],
        "partitions":[{"by":"country"}]
    }
    sur.write(df, str(out), schema=schema)
    with pytest.raises(ValueError) as ex:
        sur.validate(str(out))
    assert "country" in str(ex.value) and "enum" in str(ex.value)
