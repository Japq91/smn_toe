#!/usr/bin/env python3
"""plot03 -- Figura 3 del informe E3: figures/e3/e3_03_cambio_cajas_por_modelo.png

Cambio medio de la TSM en las cajas, modelo por modelo: arriba el cambio P - ref,
abajo el cambio relativo al trópico. Número arriba de cada columna: acuerdo de signo;
*: significativo (Wilcoxon + Holm, q10).

Entrada: estado_medio_ref<ref>.csv (q02), resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_03_cambio_cajas_por_modelo.png

Uso: python3 scripts_e3/plot03_cambio_cajas_por_modelo.py   (o bash rune3plot.sh 03)
     E3_GRUPO=40 python3 scripts_e3/plot03_cambio_cajas_por_modelo.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    est = estado()
    fig, axs = plt.subplots(2, 2, figsize=(8, 5), layout="constrained", sharey="row")
    for j, caja in enumerate(CAJAS):
        tira(axs[0, j], est, "delta", cats_fut(), "caja", caja, neutro=0, ylabel="ΔTSM [°C]")
        p0.titulo_panel(axs[0, j], LETRAS[j], f"{NOM_CAJA[caja]}\ncambio medio", pad=14)
        tira(axs[1, j], est, "delta_relativo", cats_fut(), "caja", caja, neutro=0,
             ylabel="ΔTSM - ΔTSM trópico [°C]")
        p0.titulo_panel(axs[1, j], LETRAS[2 + j], "cambio relativo al trópico", pad=14)
    leyenda_tira(fig)
    guardar(fig, "03_cambio_cajas_por_modelo")


if __name__ == "__main__":
    main()
