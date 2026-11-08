#!/usr/bin/env python3
"""Paso q09 del calculo de E3: espectro de potencia de los indices ONI,
RONI e ICEN en la referencia y en cada periodo futuro, por modelo y
escenario. Responde si cambia la periodicidad del ENOS (eventos mas o
menos espaciados), no solo su amplitud (q05).

Mismo metodo que el espectro de E2 (scripts_e2/plot04d_espectro_indices.py):
Welch con fs = 12 (frecuencia en ciclos por anio), ventana de Hann,
solapamiento del 50 % y tendencia lineal quitada en cada segmento. Lo
unico que cambia es el largo del segmento: 180 meses (15 anios) en vez
de 256. E2 analiza 115 anios; aqui cada periodo tiene 360 meses, y con
256 Welch usaria un solo segmento (los ultimos 104 meses quedarian
fuera y el estimado tendria ~2 grados de libertad). Con 180 salen 3
segmentos que cubren los 360 meses. La resolucion es 1/15 ciclos/anio:
los periodos resueltos en la banda del ENOS son 7.5, 5, 3.75, 3, 2.5 y
2.14 anios, de modo que periodo_pico_anios es discreto.

Metricas por periodo:
  periodo_pico_anios  periodo (1/f) de maxima potencia dentro de 1.5-10
                      anios, la banda donde el ENOS tiene su pico
  frac_banda_enso     fraccion de la varianza total en 2-7 anios
                      (banda clasica del ENOS)

Lee indices_enso_<escenario>_1850-2100.csv (q06).

Salidas (data/processed/e3/):
  espectro_indices_ref1985-2014.csv -- una fila por (escenario, indice,
      modelo, periodo, frecuencia): frecuencia [ciclos/anio],
      periodo_anios, potencia [degC^2 anio].
  espectro_resumen_ref1985-2014.csv -- una fila por (escenario, indice,
      modelo, periodo): periodo_pico_anios, frac_banda_enso.

Uso: python3 scripts_e3/q09_espectro.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3

INDICES = ["ONI", "RONI", "ICEN"]
NPERSEG = 180          # 15 anios: 3 segmentos en 360 meses (E2: 256 en 115 anios)
BANDA_PICO = (1.5, 10)  # anios
BANDA_ENSO = (2, 7)     # anios


def espectro(serie):
    s = serie.dropna().to_numpy()
    f, p = signal.welch(s - s.mean(), fs=12, nperseg=min(NPERSEG, len(s)), detrend="linear")
    return f[1:], p[1:]  # sin la frecuencia 0


def main():
    sel = c3.seleccion_e2()
    filas, resumen = [], []
    for esc in c3.ESCENARIOS:
        ind = pd.read_csv(c3.find_indices_csv(esc), index_col="time", parse_dates=True)
        for indice in INDICES:
            for number in sel.index:
                serie = ind[f"{number}_{indice}"]
                for per in c3.PERIODOS:
                    y0, y1 = c3.PERIODOS[per]
                    f, p = espectro(serie.loc[f"{y0}":f"{y1}"])
                    t = 1 / f
                    base = {"escenario": esc, "indice": indice, "number": number,
                            "modelo": sel.loc[number, "modelo"],
                            "seleccionado": bool(sel.loc[number, "seleccionado"]), "periodo": per}
                    filas.append(pd.DataFrame({**base, "frecuencia": f, "periodo_anios": t, "potencia": p}))
                    en_pico = (t >= BANDA_PICO[0]) & (t <= BANDA_PICO[1])
                    en_enso = (t >= BANDA_ENSO[0]) & (t <= BANDA_ENSO[1])
                    resumen.append({**base, "anios": c3.etiqueta_periodo(per),
                                    "periodo_pico_anios": float(t[en_pico][np.argmax(p[en_pico])]),
                                    "frac_banda_enso": float(p[en_enso].sum() / p.sum())})

    ref = c3.etiqueta_periodo("ref")
    esp = pd.concat(filas, ignore_index=True)
    path = c3.E3_DIR / f"espectro_indices_ref{ref}.csv"
    esp.to_csv(path, index=False, float_format="%.5g")
    print(f"Listo: {path} ({len(esp)} filas)", file=sys.stderr)

    res = pd.DataFrame(resumen)
    path = c3.E3_DIR / f"espectro_resumen_ref{ref}.csv"
    res.to_csv(path, index=False, float_format="%.4f")
    print(f"Listo: {path} ({len(res)} filas)", file=sys.stderr)
    tabla = res[res.seleccionado].groupby(["escenario", "indice", "periodo"])[
        ["periodo_pico_anios", "frac_banda_enso"]].median().unstack()
    print("Mediana de los 15 seleccionados:\n" + tabla.round(2).to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
