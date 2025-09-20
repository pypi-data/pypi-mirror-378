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
import pandas as pd
from surframe.io import write, read, encrypt

def test_encrypt_roundtrip(tmp_path):
    df = pd.DataFrame({
        "id": list(range(6)),
        "ts": pd.date_range("2024-01-01", periods=6, freq="D"),  # requerido por write()
        "country": ["AR", "AR", "BR", "CL", "CL", "AR"],
        "dni": ["10", "11", "12", "13", "14", "15"],
        "price": [5, 15, 7, 20, 30, 8],
    })
    dst = tmp_path / "demo.surx"

    # write(source, out_path, ...)
    write(df, str(dst))

    # Cifrar columna sensible
    passphrase = "secret-pass"
    encrypt(str(dst), ["dni"], passphrase)

    # Leer SIN pass (pidiendo 'dni') → debe fallar
    raised = False
    try:
        _ = read(str(dst), columns=["id", "dni"])
    except ValueError:
        raised = True
    assert raised, "Leer columna cifrada sin passphrase debe fallar"

    # Leer CON pass → rehidratación exitosa
    out = read(str(dst), columns=["id", "dni", "country"], passphrase=passphrase)
    assert {"id", "dni", "country"}.issubset(out.columns)
    assert len(out) == len(df)
    assert out.sort_values("id")["dni"].tolist() == df.sort_values("id")["dni"].tolist()
