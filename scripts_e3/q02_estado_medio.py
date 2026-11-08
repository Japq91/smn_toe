#!/usr/bin/env python3
"""Paso q02 del calculo de E3: cambio del estado medio de la TSM en
Nino 3.4, Nino 1+2 y la banda tropical, por modelo y escenario.

  delta = media(P) - media(ref),   P = P1 (2036-2065), P2 (2071-2100)
  delta_relativo = delta_caja - delta_tropical

delta_relativo dice si la caja se calienta mas (> 0) o menos (< 0) que
el promedio tropical: es la forma de separar un cambio propio del
Pacifico ecuatorial ("tipo El Nino" / "tipo La Nina") del calentamiento
general. Cada modelo se compara consigo mismo (su propia referencia), de
modo que el sesgo medio de E2 se cancela.

Lee series_cajas_1850-2100.nc (q01).

Salidas (data/processed/e3/):
  estado_medio_ref1985-2014.csv -- una fila por (modelo, escenario,
      caja, periodo futuro): tsm_ref, tsm_fut, delta, delta_relativo.
  serie_anual_anom_ref1985-2014.csv -- media anual 1850-2100 menos la
      media de la referencia, por (anio, modelo, escenario, caja): anom
      y anom_relativa (caja menos tropical). Insumo de las figuras de
      trayectorias (pluma multimodelo).

Uso: python3 scripts_e3/q02_estado_medio.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3


def main():
    ds = c3.series_cajas()
    tos = ds.tos
    ref_lbl = c3.etiqueta_periodo("ref")

    media = {p: c3.recorte(tos, p).mean("time") for p in c3.PERIODOS}
    filas = []
    for p in c3.PERIODOS_FUTUROS:
        delta = media[p] - media["ref"]
        rel = delta - delta.sel(caja="tropical")
        df = c3.xr_a_df({"tsm_ref": media["ref"], "tsm_fut": media[p], "delta": delta, "delta_relativo": rel})
        df.insert(3, "periodo", p)
        df.insert(4, "anios", c3.etiqueta_periodo(p))
        filas.append(df)
    out = pd.concat(filas, ignore_index=True)
    out = c3.agregar_modelo(out, ds)
    path = c3.E3_DIR / f"estado_medio_ref{ref_lbl}.csv"
    out.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(out)} filas)", file=sys.stderr)

    anual = tos.groupby("time.year").mean("time", skipna=False)
    anom = anual - media["ref"]
    anom_rel = anom - anom.sel(caja="tropical")
    df = c3.xr_a_df({"anom": anom, "anom_relativa": anom_rel}).dropna(subset=["anom"])
    df = c3.agregar_modelo(df, ds)
    path = c3.E3_DIR / f"serie_anual_anom_ref{ref_lbl}.csv"
    df.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(df)} filas)", file=sys.stderr)

    resumen = out[out.caja != "tropical"].groupby(["escenario", "periodo", "caja"])[["delta", "delta_relativo"]].median()
    print("Mediana de los 40 modelos [degC]:\n" + resumen.round(2).to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
