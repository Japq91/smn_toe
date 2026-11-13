#!/usr/bin/env python3
"""Paso q11 del calculo de E3: estadisticos multimodelo (por grupo de
common_e3.grupos(): 15, 40, 11 y 7) de las series, ciclos, espectros y
mapas de q02-q09, listos para graficar. Asi los scripts de figuras solo
leen y dibujan, sin calcular nada.

Para cada curva (trayectoria anual, ciclo anual, sigma movil, sigma
estacional, espectro, indice mensual): mediana, p10 y p90 entre los
modelos del grupo, y n_modelos con dato. Para los mapas: media, mediana
y acuerdo_signo por punto de grilla (fraccion de modelos con el mismo
signo que la mediana; >= 0.8 robusto, mismo criterio que q10).

La sigma movil se expresa tambien como cambio porcentual respecto de la
ventana centrada en 2000 (1985-2014, la referencia), modelo por modelo,
antes de calcular los percentiles.

Salidas (data/processed/e3/, prefijo ens_):
  ens_serie_anual_ref1985-2014.csv      grupo, escenario, caja, year
                                        x {anom, anom_relativa}
  ens_ciclo_anual_ref1985-2014.csv      grupo, escenario, caja, periodo,
                                        mes x {tsm, delta}
  ens_variabilidad_movil_30a.csv        grupo, escenario, caja,
                                        anio_central x {sigma_3m,
                                        delta_sigma_3m_pct}
  ens_variabilidad_estacional_ref1985-2014.csv
                                        grupo, escenario, caja, periodo,
                                        mes x {sigma_3m, delta_sigma_3m_pct}
  ens_espectro_ref1985-2014.csv         grupo, escenario, indice,
                                        periodo, frecuencia x {potencia}
  ens_espectro_86a.csv                  grupo, fuente, tramo (historical
                                        1929-2014 o ssp 2015-2100), indice,
                                        frecuencia x {potencia}
  ens_indices_1850-2100.csv             grupo, escenario, indice, time
                                        x {valor}
  ens_mapas_ref1985-2014.nc             (grupo, escenario, periodo, lat,
                                        lon): <var>_media, <var>_mediana,
                                        <var>_acuerdo para delta_media,
                                        delta_relativo y delta_std_pct
Columnas de los CSV: las claves, 'variable', n_modelos, mediana, p10, p90.

Uso: python3 scripts_e3/q11_ensamble.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3

REF = c3.etiqueta_periodo("ref")
ANIO_CENTRAL_REF = (c3.REF[0] + c3.REF[1] + 1) // 2   # 2000: ventana 1985-2014


def percentiles(df, claves, variables):
    """df con columna number + claves + variables -> largo por grupo."""
    partes = []
    for grupo, numeros in c3.grupos().items():
        sub = df[df["number"].isin(numeros)]
        for v in variables:
            g = sub.groupby(claves)[v]
            r = pd.DataFrame({"n_modelos": g.count(), "mediana": g.median(),
                              "p10": g.quantile(0.1), "p90": g.quantile(0.9)}).reset_index()
            r.insert(0, "grupo", grupo)
            r.insert(len(claves) + 1, "variable", v)
            partes.append(r)
    return pd.concat(partes, ignore_index=True)


def leer(nombre):
    path = c3.E3_DIR / nombre
    if not path.exists():
        sys.exit(f"Falta {path}. Correr antes los pasos q02-q09.")
    return pd.read_csv(path)


def guardar(df, nombre):
    path = c3.E3_DIR / nombre
    df.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(df)} filas)", file=sys.stderr)


def mapas():
    ds = xr.open_dataset(c3.E3_DIR / f"cambio_tsm_mapas_ref{REF}.nc")
    salida = {}
    for var in ("delta_media", "delta_relativo", "delta_std_pct"):
        med, media, acuerdo = [], [], []
        for numeros in c3.grupos().values():
            da = ds[var].sel(number=numeros)
            m = da.median("number")
            med.append(m)
            media.append(da.mean("number"))
            acuerdo.append((np.sign(da) == np.sign(m)).where(da.notnull()).mean("number"))
        g = list(c3.grupos())
        salida[f"{var}_mediana"] = xr.concat(med, dim="grupo").assign_coords(grupo=g)
        salida[f"{var}_media"] = xr.concat(media, dim="grupo").assign_coords(grupo=g)
        salida[f"{var}_acuerdo"] = xr.concat(acuerdo, dim="grupo").assign_coords(grupo=g)
        for sufijo in ("mediana", "media"):
            salida[f"{var}_{sufijo}"].attrs = dict(ds[var].attrs)
        salida[f"{var}_acuerdo"].attrs = {"units": "1", "long_name": f"Fraccion de modelos con el signo de la mediana de {var}"}
    out = xr.Dataset(salida).astype("float32")
    out = out.drop_vars([c for c in out.coords if c not in out.dims and c != "anios"])
    out.attrs = {"periodo_referencia": REF,
                 "grupos": "; ".join(f"{k}: {','.join(v)}" for k, v in c3.grupos().items())}
    path = c3.E3_DIR / f"ens_mapas_ref{REF}.nc"
    out.to_netcdf(path)
    print(f"Listo: {path}", file=sys.stderr)


def main():
    c3.silenciar_nan()

    df = leer(f"serie_anual_anom_ref{REF}.csv")
    guardar(percentiles(df, ["escenario", "caja", "year"], ["anom", "anom_relativa"]),
            f"ens_serie_anual_ref{REF}.csv")

    df = leer(f"ciclo_anual_ref{REF}.csv")
    guardar(percentiles(df, ["escenario", "caja", "periodo", "mes"], ["tsm", "delta"]),
            f"ens_ciclo_anual_ref{REF}.csv")

    df = leer("variabilidad_movil_30a.csv")
    base = df[df.anio_central == ANIO_CENTRAL_REF].set_index(["number", "escenario", "caja"])["sigma_3m"]
    df["delta_sigma_3m_pct"] = 100 * (df["sigma_3m"] / base.reindex(
        pd.MultiIndex.from_frame(df[["number", "escenario", "caja"]])).to_numpy() - 1)
    guardar(percentiles(df, ["escenario", "caja", "anio_central"], ["sigma_3m", "delta_sigma_3m_pct"]),
            "ens_variabilidad_movil_30a.csv")

    df = leer(f"variabilidad_estacional_ref{REF}.csv")
    guardar(percentiles(df, ["escenario", "caja", "periodo", "mes"], ["sigma_3m", "delta_sigma_3m_pct"]),
            f"ens_variabilidad_estacional_ref{REF}.csv")

    df = leer(f"espectro_indices_ref{REF}.csv")
    guardar(percentiles(df, ["escenario", "indice", "periodo", "frecuencia"], ["potencia"]),
            f"ens_espectro_ref{REF}.csv")

    df = leer("espectro_indices_86a.csv")
    guardar(percentiles(df, ["fuente", "tramo", "indice", "frecuencia"], ["potencia"]),
            "ens_espectro_86a.csv")

    largos = []
    for esc in c3.ESCENARIOS:
        ind = pd.read_csv(c3.find_indices_csv(esc), index_col="time", parse_dates=True)
        largo = ind.stack().rename("valor").reset_index()
        largo[["number", "indice"]] = largo["level_1"].str.split("_", n=1, expand=True)
        largo["escenario"] = esc
        largos.append(largo.drop(columns="level_1"))
    df = pd.concat(largos, ignore_index=True)
    guardar(percentiles(df, ["escenario", "indice", "time"], ["valor"]),
            f"ens_indices_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.csv")

    mapas()


if __name__ == "__main__":
    main()
