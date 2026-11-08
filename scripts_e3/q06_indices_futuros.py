#!/usr/bin/env python3
"""Paso q06 del calculo de E3: indices ONI, RONI e ICEN 1850-2100 por
modelo y escenario, con las mismas definiciones de E2 extendidas a los
datos futuros (ver common_e3.py para cada ajuste), mas dos variantes de
base fija para separar el efecto del calentamiento medio:

  ONI        anomalia Nino 3.4, bases moviles de 30 anios del CPC
             (la ultima, 2071-2100): eventos respecto del estado medio
             de su epoca.
  RONI       Nino 3.4 menos la banda tropical, base fija 1985-2014 y
             varianza igualada en la base: quita el calentamiento
             tropical sin usar bases moviles.
  ICEN       anomalia Nino 1+2, bases de 30 anios por quinquenio del
             ENFEN, sin el tope de 1991-2020 (seria un calentamiento
             leido como El Nino permanente).
  ONIfija    anomalia Nino 3.4 respecto de 1985-2014, sin quitar nada.
  ICENfija   anomalia Nino 1+2 respecto de 1985-2014, sin quitar nada.

Las tres primeras responden "¿cambia el ENOS?"; las dos fijas
responden "¿cuantos meses superan los umbrales de hoy?", que incluye
el calentamiento medio. Comparar ambas es la forma de no confundir un
cambio del estado medio con un cambio en la ocurrencia de eventos.

Lee series_cajas_1850-2100.nc (q01). Frente a indices_enso_1900-2014.csv
de E2: el ONI y el ICEN coinciden hasta ~1985; despues difieren porque
las bases moviles cercanas a 2014 ya no se truncan en 2014 sino que
usan datos del escenario. El RONI difiere en toda la serie por un
factor de escala constante (calculado en la base, ver
common_e3.roni_index).

Salida: data/processed/e3/indices_enso_<escenario>_1850-2100.csv, uno
por escenario, con el mismo formato que el de E2: indice temporal y
columnas M01_ONI, M01_RONI, M01_ICEN, M01_ONIfija, M01_ICENfija, ...

Uso: python3 scripts_e3/q06_indices_futuros.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3

INDICES = ["ONI", "RONI", "ICEN", "ONIfija", "ICENfija"]


def indices_modelo(tos):
    """tos: DataArray (caja, time) de un modelo y escenario."""
    n34, n12, trop = (tos.sel(caja=k).drop_vars("caja") for k in ("nino34", "nino12", "tropical"))
    # Las bases moviles se ajustan al rango con datos: CAMS-CSM1-0 e
    # IITM-ESM terminan en 2099, asi que su ultima base es 2070-2099.
    n34v, n12v = n34.dropna("time"), n12.dropna("time")
    return {
        "ONI": c3.oni_index(n34v),
        "RONI": c3.roni_index(n34, trop),
        "ICEN": c3.icen_index(n12v),
        "ONIfija": c3.indice_base_fija(n34),
        "ICENfija": c3.indice_base_fija(n12),
    }


def main():
    ds = c3.series_cajas()
    for esc in c3.ESCENARIOS:
        print(f"  {esc} ...", file=sys.stderr)
        cols = {}
        for number in ds.number.values:
            tos = ds.tos.sel(number=number, escenario=esc).load()
            for k, da in indices_modelo(tos).items():
                cols[f"{number}_{k}"] = da.to_pandas()
        df = pd.DataFrame(cols)
        df.index.name = "time"
        df = df.sort_index().dropna(how="all")
        path = c3.E3_DIR / f"indices_enso_{esc}_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.csv"
        df.to_csv(path, float_format="%.4f")
        print(f"Listo: {path} ({df.shape[0]} filas, {df.shape[1]} columnas)", file=sys.stderr)


if __name__ == "__main__":
    main()
