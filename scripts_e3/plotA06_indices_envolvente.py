#!/usr/bin/env python3
"""plotA06 -- Figura A6 del informe E3: figures/e3/e3_A06_indices_envolvente.png

Índices ONI, RONI e ICEN mensuales 1950-2100: mediana y p10-p90 del grupo y, en
negro, la serie del primer modelo de la selección del E2, para SSP2-4.5 y SSP5-8.5.

Entrada: ens_indices_<inicio>-<fin>.csv (q11), indices_enso de q06 (data/processed/e3/)
Salida: figures/e3/e3_A06_indices_envolvente.png

Uso: python3 scripts_e3/plotA06_indices_envolvente.py   (o bash rune3plot.sh A06)
     E3_GRUPO=40 python3 scripts_e3/plotA06_indices_envolvente.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig = figura_indices(INDICES, "Índices ENOS 1950-2100 (bases móviles y RONI)")
    guardar(fig, "A06_indices_envolvente")


if __name__ == "__main__":
    main()
