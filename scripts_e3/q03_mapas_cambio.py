#!/usr/bin/env python3
"""Paso q03 del calculo de E3: mapas de cambio de la TSM (campo 2D
completo de data/processed/masked/, lat 30S-30N, todas las longitudes)
por modelo, escenario y periodo futuro.

Tres campos por punto de grilla:

  delta_media = media(P) - media(ref)                              [degC]
  delta_relativo = delta_media - <delta_media>_tropical             [degC]
      <.>_tropical = promedio 20S-20N ponderado por cos(lat), la misma
      banda del RONI. Muestra el patron del calentamiento (donde se
      calienta mas o menos que el promedio tropical), sin la parte
      uniforme.
  delta_std_pct = 100 * (sigma(P) - sigma(ref)) / sigma(ref)           [%]
      sigma = desviacion estandar de la anomalia sin tendencia de cada
      periodo (common_e3.anomalia_sin_tendencia): cambio de la
      variabilidad interanual, mismo cociente que p04 de E2 pero entre
      periodos del mismo modelo, no contra ERSSTv5.

Salida: data/processed/e3/cambio_tsm_mapas_ref1985-2014.nc
  delta_media, delta_relativo, delta_std_pct (number, escenario,
  periodo, lat, lon); sigma_ref (number, lat, lon); coordenadas model y
  seleccionado sobre number.

Uso: python3 scripts_e3/q03_mapas_cambio.py
"""
import sys
from pathlib import Path

import numpy as np
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3


def media_tropical(campo):
    banda = campo.sel(lat=slice(20, -20)) if campo.lat[0] > campo.lat[-1] else campo.sel(lat=slice(-20, 20))
    return banda.weighted(np.cos(np.deg2rad(banda.lat))).mean(("lat", "lon"))


def main():
    c3.silenciar_nan()
    registro = c3.read_model_registry()
    sel = c3.seleccion_e2()

    d_media, d_rel, d_std, s_ref = [], [], [], []
    for row in registro:
        number, model = row["number"], row["model"]
        print(f"  {number} {model} ...", file=sys.stderr)
        por_esc_m, por_esc_r, por_esc_s = [], [], []
        for esc in c3.ESCENARIOS:
            campo = c3.campo_completo(model, esc)
            ref = c3.recorte(campo, "ref").load()
            media_ref = ref.mean("time")
            sigma_ref = c3.anomalia_sin_tendencia(ref).std("time", ddof=1)
            pm, pr, ps = [], [], []
            for p in c3.PERIODOS_FUTUROS:
                fut = c3.recorte(campo, p).load()
                dm = fut.mean("time") - media_ref
                pm.append(dm)
                pr.append(dm - media_tropical(dm))
                sigma = c3.anomalia_sin_tendencia(fut).std("time", ddof=1)
                ps.append(100 * (sigma - sigma_ref) / sigma_ref)
            por_esc_m.append(xr.concat(pm, dim="periodo"))
            por_esc_r.append(xr.concat(pr, dim="periodo"))
            por_esc_s.append(xr.concat(ps, dim="periodo"))
        d_media.append(xr.concat(por_esc_m, dim="escenario"))
        d_rel.append(xr.concat(por_esc_r, dim="escenario"))
        d_std.append(xr.concat(por_esc_s, dim="escenario"))
        s_ref.append(sigma_ref)  # la referencia es historical: igual en ambos escenarios

    numbers = [r["number"] for r in registro]
    coords = dict(number=numbers, escenario=c3.ESCENARIOS, periodo=c3.PERIODOS_FUTUROS)

    def armar(lista, nombre, unidades, largo):
        da = xr.concat(lista, dim="number").assign_coords(coords).astype("float32")
        da = da.drop_vars([c for c in da.coords if c not in da.dims])
        da.name = nombre
        da.attrs = {"units": unidades, "long_name": largo}
        return da

    ds = xr.merge([
        armar(d_media, "delta_media", "degC", "Cambio de la TSM media, P - ref"),
        armar(d_rel, "delta_relativo", "degC", "Cambio de la TSM media menos su promedio tropical 20S-20N"),
        armar(d_std, "delta_std_pct", "%", "Cambio porcentual de sigma de la anomalia sin tendencia, P vs ref"),
    ])
    ds.attrs = {}  # merge copia los attrs de la primera variable al dataset
    sr = xr.concat(s_ref, dim="number").assign_coords(number=numbers).astype("float32")
    ds["sigma_ref"] = sr.drop_vars([c for c in sr.coords if c not in sr.dims])
    ds["sigma_ref"].attrs = {"units": "degC", "long_name": "sigma de la anomalia sin tendencia en ref"}
    ds = ds.assign_coords(
        model=("number", [r["model"] for r in registro]),
        seleccionado=("number", np.array([bool(sel.loc[n, "seleccionado"]) for n in numbers])),
        anios=("periodo", [c3.etiqueta_periodo(p) for p in c3.PERIODOS_FUTUROS]))
    ds.attrs["periodo_referencia"] = c3.etiqueta_periodo("ref")
    ds.attrs["descripcion"] = ("Cambio de la TSM media y de su variabilidad interanual por punto de grilla, "
                               "cada modelo contra su propia referencia historical.")

    out = c3.E3_DIR / f"cambio_tsm_mapas_ref{c3.etiqueta_periodo('ref')}.nc"
    ds.to_netcdf(out)
    print(f"Listo: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
