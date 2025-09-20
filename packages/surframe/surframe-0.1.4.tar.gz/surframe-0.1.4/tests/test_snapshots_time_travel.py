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


# tests/test_snapshots_time_travel.py
import os
from datetime import datetime, timezone
from tempfile import TemporaryDirectory

import pandas as pd
import surframe as sur


def _make_df():
    # Igual al dataset de ejemplo:
    # AR: 3 filas con price > 10
    # CL: 2 filas con price < 10
    # UY: 1 fila con price ~9
    return pd.DataFrame(
        {
            "ts": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                    "2025-02-01",
                    "2025-01-03",
                    "2025-02-10",
                    "2025-01-04",
                ],
                utc=True,
            ),
            "country": ["AR", "AR", "AR", "CL", "CL", "UY"],
            "price": [10.5, 12.0, 11.3, 8.7, 7.9, 9.1],
        }
    )


def test_time_travel_with_reindex_pruning():
    with TemporaryDirectory() as td:
        path = os.path.join(td, "sales.surx")
        df = _make_df()

        # 1) write sin snapshot automático (control explícito)
        sur.write(df, path, schema=None, indexes=None, auto_snapshot=False)

        # 2) snapshot S1 (baseline: SOLO ts.minmax y country.bloom)
        s1 = sur.snapshot(path, note="baseline")
        ts1 = s1["ts"]

        # Verificación de plan con as_of=S1 (price no indexado aún)
        plan_s1 = sur.plan(path, where="price>10", as_of=ts1)
        assert plan_s1["indexes"]["minmax"]["price_indexed"] is False
        # sin índice de price: no puede prunear → 3 candidatos
        assert plan_s1["candidates_count"] == 3
        assert sorted(plan_s1["candidates_final"]) == ["000000", "000001", "000002"]

        # 3) reindex price:minmax y snapshot S2
        sur.reindex(path, {"price": {"minmax": {}}})
        s2 = sur.snapshot(path, note="with price.minmax")
        ts2 = s2["ts"]

        # 4) Plan "as_of" S1 debe ignorar el índice nuevo
        plan_s1_again = sur.plan(path, where="price>10", as_of=ts1)
        assert plan_s1_again["indexes"]["minmax"]["price_indexed"] is False
        assert plan_s1_again["candidates_count"] == 3

        # 5) Plan "as_of" S2 (o latest) sí usa price.minmax → prunea a 1 chunk (AR)
        plan_s2 = sur.plan(path, where="price>10", as_of=ts2)
        assert plan_s2["indexes"]["minmax"]["price_indexed"] is True
        assert plan_s2["candidates_count"] == 1
        assert plan_s2["candidates_final"] == ["000000"]  # AR

        # 6) Lecturas consistentes (contenido), independiente de as_of
        df_latest = sur.read(path, columns=["ts", "country", "price"], where="price>10", as_of=ts2)
        df_old = sur.read(path, columns=["ts", "country", "price"], where="price>10", as_of=ts1)
        assert len(df_latest) == 3
        assert len(df_old) == 3
        # orden por ts creciente
        assert df_latest["ts"].is_monotonic_increasing
        assert df_old["ts"].is_monotonic_increasing
