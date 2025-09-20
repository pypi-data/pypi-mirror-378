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


import numpy as np, pandas as pd, surframe as sur

def test_ann_flat_roundtrip(tmp_path):
    # dataset chiquito con embedding D=4
    df = pd.DataFrame({
        "id": [0,1,2,3],
        "embedding": [
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1],
        ],
        "country": ["AR","AR","BR","CL"],
    })
    p = tmp_path/"mini.surx"
    sur.write(df, str(p))
    sur.ann_build(str(p), col="embedding", metric="cosine", dim=4)
    q = [1,0,0,0]
    out = sur.vsearch(str(p), query_vec=q, k=2, columns=["id","country"])
    assert list(out["id"]) == [0,1]  # 0 más cercano, 1 empate siguiente
