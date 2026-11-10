#!/usr/bin/env python3
"""plotA03 -- Figura A3 del informe E3: figures/e3/e3_A03_cambio_amplitud_por_modelo.png

Cambio de la amplitud del ciclo anual (máximo menos mínimo de la climatología
mensual) en Niño 3.4 y Niño 1+2, modelo por modelo.

Entrada: ciclo_anual_amplitud_ref<ref>.csv (q04), resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_A03_cambio_amplitud_por_modelo.png

Uso: python3 scripts_e3/plotA03_cambio_amplitud_por_modelo.py   (o bash rune3plot.sh A03)
     E3_GRUPO=40 python3 scripts_e3/plotA03_cambio_amplitud_por_modelo.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for j, caja in enumerate(CAJAS):
        tira(axs[j], amplitud(), "delta_amplitud", cats_fut(), "caja", caja, neutro=0, ylabel="Δ amplitud [°C]")
        p0.titulo_panel(axs[j], LETRAS[j], NOM_CAJA[caja], pad=14)
    leyenda_tira(fig)
    guardar(fig, "A03_cambio_amplitud_por_modelo")


if __name__ == "__main__":
    main()
