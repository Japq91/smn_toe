#!/usr/bin/env python3
"""Paso p11 del calculo de E2: seleccion final de modelos.

Seleccion = los modelos que pasan el filtro de eventos (p10,
pruebas_eventos_<y0>-<y1>.csv): ninguna de las 6 pruebas de frecuencia,
duracion y estacionalidad de los eventos de RONI e ICEN se rechaza con
la correccion de Holm (columna pasa_filtro). Su regimen de eventos no se
distingue estadisticamente del de ERSSTv5. Con el periodo 1900-2014 son
15 de los 40 modelos.

Dentro de la seleccion, los modelos se ordenan por S_final (p09,
skill_score_vent<V>m_<y0>-<y1>.csv) de la ventana principal de +-12
meses (columna puesto, 1 = mejor). S ya no corta: hasta 2026-10-31 se
exigia ademas S_final >= 0.9 y S_ICEN >= 0.9 (7 modelos); ese criterio
queda como columna informativa cumple_s09. Como el filtro no depende de
la ventana del compuesto, la seleccion es la misma con +-15 y +-18
meses; lo que cambia con la ventana es el orden (puesto_15, puesto_18).

Salida: seleccion_<y0>-<y1>.csv, una fila por modelo, ordenada por
S_final de +-12 meses. Columnas: modelo, pasa_filtro, rechazadas,
S_ONI, S_RONI, S_ICEN, S_final (+-12), S_final_15, S_ICEN_15,
S_final_18, S_ICEN_18, seleccionado, puesto, puesto_15, puesto_18
(orden por S_final entre los seleccionados; vacio si no lo esta) y
cumple_s09 (S_final >= 0.9 y S_ICEN >= 0.9 con +-12 meses).

Uso:
    python3 scripts_e2/p11_seleccion.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e2 as c2

# Umbral anterior (hasta 2026-10-31), solo informativo: columna cumple_s09.
S_MIN = 0.9
S_ICEN_MIN = 0.9
VENTANA = 12
VENTANAS_SENS = [15, 18]


def main():
    periodo = c2.indices_period()
    rutas = {"filtro": c2.E2_DIR / f"pruebas_eventos_{periodo}.csv"}
    rutas.update({v: c2.E2_DIR / f"skill_score_vent{v}m_{periodo}.csv" for v in [VENTANA] + VENTANAS_SENS})
    for r in rutas.values():
        if not r.exists():
            sys.exit(f"Falta {r}. Correr antes p09_skill_score.py (12, 15 y 18) y p10_pruebas_eventos.py.")

    filtro = pd.read_csv(rutas["filtro"], index_col="number").drop(index="OBS")
    filtro["pasa_filtro"] = filtro["pasa_filtro"].astype(str) == "True"
    sk = {v: pd.read_csv(rutas[v], index_col="number") for v in [VENTANA] + VENTANAS_SENS}
    registro = {r["number"]: r["model"] for r in c2.read_model_registry()}

    df = pd.DataFrame(index=sk[VENTANA].index)
    df["modelo"] = df.index.map(registro)
    df["pasa_filtro"] = filtro.loc[df.index, "pasa_filtro"]
    df["rechazadas"] = filtro.loc[df.index, "rechazadas"].fillna("")
    for c in ["S_ONI", "S_RONI", "S_ICEN", "S_final"]:
        df[c] = sk[VENTANA][c]
    for v in VENTANAS_SENS:
        df[f"S_final_{v}"] = sk[v]["S_final"]
        df[f"S_ICEN_{v}"] = sk[v]["S_ICEN"]

    df["seleccionado"] = df["pasa_filtro"]
    for v, col in [(VENTANA, "S_final")] + [(v, f"S_final_{v}") for v in VENTANAS_SENS]:
        nombre = "puesto" if v == VENTANA else f"puesto_{v}"
        df[nombre] = df.loc[df["seleccionado"], col].rank(ascending=False, method="min").astype("Int64")
    df["cumple_s09"] = (df["S_final"] >= S_MIN) & (df["S_ICEN"] >= S_ICEN_MIN)
    df = df.sort_values("S_final", ascending=False)

    sel = df.index[df["seleccionado"]].tolist()
    print(f"  Seleccion (pasan el filtro de eventos): {len(sel)} de {len(df)} -> {', '.join(sel)}", file=sys.stderr)
    print(f"  De ellos con S_final >= {S_MIN} y S_ICEN >= {S_ICEN_MIN} (+-{VENTANA} m): "
          f"{', '.join(df.index[df['seleccionado'] & df['cumple_s09']])}", file=sys.stderr)
    for v in VENTANAS_SENS:
        rho = df.loc[df["seleccionado"], ["puesto", f"puesto_{v}"]].astype(float).corr("spearman").iloc[0, 1]
        print(f"  Orden con +-{v} m vs +-{VENTANA} m (Spearman, seleccionados): {rho:.2f}", file=sys.stderr)

    out = c2.E2_DIR / f"seleccion_{periodo}.csv"
    df.to_csv(out, float_format="%.4f")
    print(f"Listo: {out}")


if __name__ == "__main__":
    main()
