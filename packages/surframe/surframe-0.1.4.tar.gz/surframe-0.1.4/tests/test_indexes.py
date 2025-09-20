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
from surframe.indexes import build_minmax_index, query_minmax, build_bloom_index, query_bloom

def test_minmax_api():
    idx = build_minmax_index({"c1": [1, 5, 2], "c2": [10, 20]})
    assert idx["c1"] == (1, 5)
    assert set(query_minmax(idx, ">=", 5)) >= {"c1", "c2"}

def test_bloom_api():
    idx = build_bloom_index({"c1": ["AR", "CL"], "c2": ["UY"]}, fp_rate=0.01)
    cands = set(query_bloom(idx, "AR"))
    assert "c1" in cands
