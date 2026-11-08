#!/usr/bin/env python3
"""Paso q04 del calculo de E3: ciclo anual de la TSM en Nino 3.4 y
Nino 1+2 (y la banda tropical, como contraste) en la referencia y en
cada periodo futuro, por modelo y escenario.

  C_m(P) = media de los meses m del periodo P            (m = 1..12)
  amplitud = max_m C_m - min_m C_m

El ciclo anual importa sobre todo en Nino 1+2: su amplitud (~4-5 degC
observados) condiciona la estacionalidad del El Nino costero, y un
debilitamiento o adelanto del maximo de verano cambiaria cuando son
probables los eventos. Igual que en q02, cada modelo se compara consigo
mismo.

Lee series_cajas_1850-2100.nc (q01).

Salidas (data/processed/e3/):
  ciclo_anual_ref1985-2014.csv -- una fila por (modelo, escenario,
      caja, periodo, mes): tsm, delta (C_m(P) - C_m(ref); 0 en ref).
  ciclo_anual_amplitud_ref1985-2014.csv -- una fila por (modelo,
      escenario, caja, periodo): amplitud, mes_max, mes_min y
      delta_amplitud respecto de ref.

Uso: python3 scripts_e3/q04_ciclo_anual.py
"""
import sys
from pathlib import Path

import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3


def main():
    ds = c3.series_cajas()
    ref_lbl = c3.etiqueta_periodo("ref")
    periodos = list(c3.PERIODOS)

    clim = xr.concat([c3.recorte(ds.tos, p).groupby("time.month").mean("time") for p in periodos],
                     dim="periodo").assign_coords(periodo=periodos)
    delta = clim - clim.sel(periodo="ref")

    df = c3.xr_a_df({"tsm": clim, "delta": delta}).rename(columns={"month": "mes"})
    df = c3.agregar_modelo(df, ds)[["number", "modelo", "seleccionado", "escenario", "caja",
                                    "periodo", "mes", "tsm", "delta"]]
    path = c3.E3_DIR / f"ciclo_anual_ref{ref_lbl}.csv"
    df.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(df)} filas)", file=sys.stderr)

    amp = clim.max("month") - clim.min("month")
    resumen = c3.xr_a_df({
        "amplitud": amp,
        "delta_amplitud": amp - amp.sel(periodo="ref"),
        "mes_max": clim.idxmax("month"),
        "mes_min": clim.idxmin("month"),
    })
    resumen = c3.agregar_modelo(resumen, ds)
    resumen[["mes_max", "mes_min"]] = resumen[["mes_max", "mes_min"]].astype(int)
    resumen.insert(resumen.columns.get_loc("periodo") + 1, "anios",
                   resumen["periodo"].map(c3.etiqueta_periodo))
    path = c3.E3_DIR / f"ciclo_anual_amplitud_ref{ref_lbl}.csv"
    resumen.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(resumen)} filas)", file=sys.stderr)

    tabla = resumen[resumen.caja != "tropical"].groupby(["escenario", "periodo", "caja"])["amplitud"].median()
    print("Amplitud del ciclo anual, mediana de los 40 modelos [degC]:\n" + tabla.round(2).to_string(),
          file=sys.stderr)


if __name__ == "__main__":
    main()
