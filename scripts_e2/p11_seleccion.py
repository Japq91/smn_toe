#!/usr/bin/env python3
"""Paso p11 del calculo de E2: seleccion final de modelos.

Combina los dos criterios del E2 en un solo paso:

1. Filtro de eventos (p10, pruebas_eventos_<y0>-<y1>.csv): el modelo
   pasa si ninguna de las 6 pruebas de frecuencia, duracion y
   estacionalidad de los eventos de RONI e ICEN se rechaza con la
   correccion de Holm (columna pasa_filtro). Su regimen de eventos no
   se distingue estadisticamente del de ERSSTv5.

2. Umbral de skill score (p09, skill_score_vent<V>m_<y0>-<y1>.csv):

       S_final >= S_MIN      y      S_ICEN >= S_ICEN_MIN

   con S_MIN = S_ICEN_MIN = 0.9. Como en el compuesto r ~ 1, S depende
   sobre todo de sigma_hat (amplitud del evento tipico del modelo /
   observada). Despejando sigma_hat de S = 2 (1 + r) / (sigma_hat +
   1/sigma_hat)^2 con r = 1, S >= 0.9 equivale a 0.72 <= sigma_hat <=
   1.39 (con r = 0.97, entre 0.74 y 1.35): un evento tipico entre ~26 %
   mas debil y ~35 % mas intenso que el observado. Es un umbral con
   significado fisico, a diferencia del percentil 75 usado antes, que
   deja siempre la cuarta parte de los modelos. La condicion sobre
   S_ICEN evita que un modelo entre solo por su desempeño en Nino 3.4
   (S_ONI y S_RONI altos) con un Nino costero tipico demasiado debil;
   con ella no hace falta ponderar el ICEN dentro de S_final, que sigue
   siendo el promedio simple de S_ONI, S_RONI y S_ICEN.

Seleccionado = pasa_filtro y S_final >= 0.9 y S_ICEN >= 0.9, con la
ventana principal de +-12 meses. Las ventanas de +-15 y +-18 meses se
evaluan con el mismo criterio como prueba de sensibilidad (el filtro de
eventos no depende de la ventana).

Salida: seleccion_<y0>-<y1>.csv, una fila por modelo, ordenada por
S_final de +-12 meses. Columnas: modelo, pasa_filtro, rechazadas,
S_ONI, S_RONI, S_ICEN, S_final (+-12), S_final_15, S_ICEN_15,
S_final_18, S_ICEN_18, seleccionado, seleccionado_15, seleccionado_18
y n_ventanas (en cuantas de las tres ventanas queda seleccionado).

Uso:
    python3 scripts_e2/p11_seleccion.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e2 as c2

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

    def criterio(s_final, s_icen):
        return df["pasa_filtro"] & (s_final >= S_MIN) & (s_icen >= S_ICEN_MIN)

    df["seleccionado"] = criterio(df["S_final"], df["S_ICEN"])
    for v in VENTANAS_SENS:
        df[f"seleccionado_{v}"] = criterio(df[f"S_final_{v}"], df[f"S_ICEN_{v}"])
    df["n_ventanas"] = df[["seleccionado"] + [f"seleccionado_{v}" for v in VENTANAS_SENS]].sum(axis=1)
    df = df.sort_values("S_final", ascending=False)

    sel = df.index[df["seleccionado"]].tolist()
    print(f"  Pasan el filtro de eventos: {int(df['pasa_filtro'].sum())} de {len(df)}", file=sys.stderr)
    print(f"  Seleccion (filtro + S_final >= {S_MIN} + S_ICEN >= {S_ICEN_MIN}, +-{VENTANA} m): "
          f"{len(sel)} -> {', '.join(sel)}", file=sys.stderr)
    for v in VENTANAS_SENS:
        sv = df.index[df[f"seleccionado_{v}"]].tolist()
        print(f"  Con +-{v} m: {len(sv)} -> {', '.join(sv)}", file=sys.stderr)

    out = c2.E2_DIR / f"seleccion_{periodo}.csv"
    df.to_csv(out, float_format="%.4f")
    print(f"Listo: {out}")


if __name__ == "__main__":
    main()
