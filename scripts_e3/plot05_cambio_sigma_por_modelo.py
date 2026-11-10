#!/usr/bin/env python3
"""plot05 -- Figura 5 del informe E3: figures/e3/e3_05_cambio_sigma_por_modelo.png

Cambio porcentual de σ3m (desviación estándar de la anomalía suavizada a 3 meses,
la escala del ONI y del ICEN) en Niño 3.4 y Niño 1+2, modelo por modelo.

Entrada: variabilidad_cajas_ref<ref>.csv (q05), resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_05_cambio_sigma_por_modelo.png

Uso: python3 scripts_e3/plot05_cambio_sigma_por_modelo.py   (o bash rune3plot.sh 05)
     E3_GRUPO=40 python3 scripts_e3/plot05_cambio_sigma_por_modelo.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for j, caja in enumerate(CAJAS):
        tira(axs[j], variab(), "delta_sigma_3m_pct", cats_fut(), "caja", caja, neutro=0, ylabel="Δσ$_{3m}$ [%]")
        p0.titulo_panel(axs[j], LETRAS[j], NOM_CAJA[caja], pad=14)
    leyenda_tira(fig)
    guardar(fig, "05_cambio_sigma_por_modelo")


if __name__ == "__main__":
    main()
