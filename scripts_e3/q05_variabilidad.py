#!/usr/bin/env python3
"""Paso q05 del calculo de E3: cambio de la variabilidad interanual de
la TSM en Nino 3.4 y Nino 1+2 (y la banda tropical, como contraste),
por modelo y escenario.

La anomalia de cada ventana de 30 anios se calcula quitando la
climatologia mensual de esa misma ventana y su tendencia lineal
(common_e3.anomalia_sin_tendencia): asi la variabilidad no queda
inflada por el calentamiento dentro de la ventana. Sobre esa anomalia:

  sigma      desviacion estandar de la anomalia mensual          [degC]
  sigma_3m   idem, de la media movil de 3 meses (escala del ONI/ICEN)
  asimetria  coeficiente de asimetria (skewness) de la anomalia
             mensual: > 0 = eventos calidos mas intensos que los frios,
             rasgo observado del ENOS, mas marcado en Nino 1+2
  curtosis   exceso de curtosis (colas pesadas = mas extremos)
  delta_sigma_pct = 100 * (sigma(P) - sigma(ref)) / sigma(ref)

Tres salidas a partir de lo mismo:
  - por periodo (ref, P1, P2), para tablas y diagramas de caja;
  - por periodo y mes calendario: sigma_3m de cada estacion de 3 meses
    (centrada en el mes), es decir, en que epoca del ano se concentra
    la variabilidad. El ENOS observado tiene su maximo en noviembre-
    enero en Nino 3.4 y en el verano austral en Nino 1+2; un corrimiento
    de ese maximo cambiaria cuando son mas probables los eventos;
  - en ventana movil de 30 anios (paso de 1 anio, centrada), para ver
    cuando empieza a cambiar la variabilidad y comparar con la
    trayectoria de la media (q02).

Lee series_cajas_1850-2100.nc (q01).

Salidas (data/processed/e3/):
  variabilidad_cajas_ref1985-2014.csv -- una fila por (modelo,
      escenario, caja, periodo): sigma, sigma_3m, asimetria, curtosis,
      delta_sigma_pct, delta_sigma_3m_pct.
  variabilidad_estacional_ref1985-2014.csv -- una fila por (modelo,
      escenario, caja, periodo, mes): sigma_3m, delta_sigma_3m_pct.
  variabilidad_movil_30a.csv -- una fila por (modelo, escenario, caja,
      anio_central): sigma, sigma_3m, asimetria.

Uso: python3 scripts_e3/q05_variabilidad.py
"""
import sys
from pathlib import Path

import pandas as pd
import xarray as xr
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3

VENTANA = 30  # anios de la ventana movil (el mismo largo que ref, P1 y P2)


def metricas(tos_ventana):
    """Dict de DataArrays (number, escenario, caja) con las metricas de
    una ventana de anios."""
    anom = c3.anomalia_sin_tendencia(tos_ventana)
    a3 = c3.c2.rolling3(anom)
    eje = anom.get_axis_num("time")
    sk = stats.skew(anom.values, axis=eje, nan_policy="omit")
    ku = stats.kurtosis(anom.values, axis=eje, nan_policy="omit")
    plantilla = anom.isel(time=0, drop=True)
    return {
        "sigma": anom.std("time", ddof=1),
        "sigma_3m": a3.std("time", ddof=1),
        "asimetria": plantilla.copy(data=sk),
        "curtosis": plantilla.copy(data=ku),
    }


def main():
    c3.silenciar_nan()  # ventanas sin datos (modelos que empiezan despues de 1850)
    ds = c3.series_cajas()
    tos = ds.tos.load()
    ref_lbl = c3.etiqueta_periodo("ref")

    por_periodo = {p: metricas(c3.recorte(tos, p)) for p in c3.PERIODOS}
    filas = []
    for p, m in por_periodo.items():
        ref = por_periodo["ref"]
        m = dict(m)
        m["delta_sigma_pct"] = 100 * (m["sigma"] - ref["sigma"]) / ref["sigma"]
        m["delta_sigma_3m_pct"] = 100 * (m["sigma_3m"] - ref["sigma_3m"]) / ref["sigma_3m"]
        df = c3.xr_a_df(m)
        df.insert(3, "periodo", p)
        df.insert(4, "anios", c3.etiqueta_periodo(p))
        filas.append(df)
    out = c3.agregar_modelo(pd.concat(filas, ignore_index=True), ds)
    path = c3.E3_DIR / f"variabilidad_cajas_ref{ref_lbl}.csv"
    out.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(out)} filas)", file=sys.stderr)

    tabla = out[(out.caja != "tropical") & (out.periodo != "ref")].groupby(
        ["escenario", "periodo", "caja"])["delta_sigma_3m_pct"].agg(
        mediana="median", modelos_aumentan=lambda x: int((x > 0).sum()))
    print("Cambio de sigma_3m [%], 40 modelos:\n" + tabla.round(1).to_string(), file=sys.stderr)

    est = {}
    for p in c3.PERIODOS:
        a3 = c3.c2.rolling3(c3.anomalia_sin_tendencia(c3.recorte(tos, p)))
        est[p] = a3.groupby("time.month").std("time", ddof=1)
    filas = []
    for p, sig in est.items():
        df = c3.xr_a_df({"sigma_3m": sig,
                         "delta_sigma_3m_pct": 100 * (sig - est["ref"]) / est["ref"]})
        df.insert(3, "periodo", p)
        filas.append(df.rename(columns={"month": "mes"}))
    est_df = c3.agregar_modelo(pd.concat(filas, ignore_index=True), ds)
    path = c3.E3_DIR / f"variabilidad_estacional_ref{ref_lbl}.csv"
    est_df.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(est_df)} filas)", file=sys.stderr)

    print(f"  Ventana movil de {VENTANA} anios ...", file=sys.stderr)
    movil = []
    for y0 in range(c3.ANIO_INICIO, c3.ANIO_FIN - VENTANA + 2):
        v = tos.sel(time=slice(f"{y0}", f"{y0 + VENTANA - 1}"))
        m = metricas(v)
        df = c3.xr_a_df({k: m[k] for k in ("sigma", "sigma_3m", "asimetria")})
        df.insert(3, "anio_central", y0 + VENTANA // 2)
        movil.append(df)
    movil = c3.agregar_modelo(pd.concat(movil, ignore_index=True), ds)
    path = c3.E3_DIR / f"variabilidad_movil_{VENTANA}a.csv"
    movil.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(movil)} filas)", file=sys.stderr)


if __name__ == "__main__":
    main()
