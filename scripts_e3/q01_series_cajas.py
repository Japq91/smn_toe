#!/usr/bin/env python3
"""Paso q01 del calculo de E3: series mensuales crudas (degC) de
Nino 3.4, Nino 1+2 y la banda tropical 20S-20N, historical + SSP
concatenados (1850-2100), para los 40 modelos y los escenarios de
common_e3.ESCENARIOS.

Es la base de q02 (estado medio), q04 (ciclo anual), q05
(variabilidad) y q06 (indices): se extraen las cajas una sola vez en
vez de releer los NetCDF de masked/ en cada paso. Promedios por caja
con el mismo criterio que E2 (common_e2.box_series: promedio simple en
Nino 3.4 y Nino 1+2, ponderado por cos(lat) en la banda tropical).

El tramo historico (1850-2014) se repite en cada escenario: asi cada
serie escenario es continua y se puede tratar por separado.

Salida: data/processed/e3/series_cajas_1850-2100.nc
  tos(number, escenario, caja, time) [degC]; coordenadas auxiliares
  model y seleccionado (los 15 de E2) sobre number.

Uso: python3 scripts_e3/q01_series_cajas.py
"""
import sys
from pathlib import Path

import numpy as np
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3


def main():
    c3.E3_DIR.mkdir(parents=True, exist_ok=True)
    registro = c3.read_model_registry()
    sel = c3.seleccion_e2()
    cajas = list(c3.BOXES)

    por_modelo = []
    for row in registro:
        number, model = row["number"], row["model"]
        print(f"  {number} {model} ...", file=sys.stderr)
        por_esc = [xr.concat([c3.serie_completa(model, esc, k) for k in cajas], dim="caja")
                   for esc in c3.ESCENARIOS]
        por_modelo.append(xr.concat(por_esc, dim="escenario"))

    numbers = [r["number"] for r in registro]
    tos = xr.concat(por_modelo, dim="number").assign_coords(
        number=numbers, escenario=c3.ESCENARIOS, caja=cajas)
    tos = tos.transpose("number", "escenario", "caja", "time").astype("float32")
    tos.name = "tos"
    tos.attrs = {"units": "degC", "long_name": "TSM promedio de la caja (historical + escenario)"}

    ds = tos.to_dataset()
    ds = ds.assign_coords(
        model=("number", [r["model"] for r in registro]),
        seleccionado=("number", np.array([bool(sel.loc[n, "seleccionado"]) for n in numbers])))
    ds.attrs["descripcion"] = (
        "Series mensuales por caja; historical hasta 2014-12 y el escenario desde 2015-01. "
        "nino34: 5S-5N 170W-120W, nino12: 10S-0 90W-80W (promedio simple); "
        "tropical: 20S-20N todas las longitudes (ponderado por cos(lat)).")
    ds.attrs["periodos"] = "; ".join(f"{k}={c3.etiqueta_periodo(k)}" for k in c3.PERIODOS)

    out = c3.E3_DIR / f"series_cajas_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.nc"
    ds.to_netcdf(out)
    faltan = int(ds.tos.isel(caja=0).isnull().sum("time").max())
    print(f"Listo: {out} ({ds.sizes['number']} modelos, {ds.sizes['escenario']} escenarios; "
          f"max meses sin dato por serie: {faltan})", file=sys.stderr)


if __name__ == "__main__":
    main()
