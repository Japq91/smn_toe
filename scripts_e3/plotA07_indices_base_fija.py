#!/usr/bin/env python3
"""plotA07 -- Figura A7 del informe E3: figures/e3/e3_A07_indices_base_fija.png

Índices ONIfija e ICENfija (anomalía respecto de 1985-2014 sin quitar el
calentamiento), mismo formato que la Figura A6.

Entrada: ens_indices_<inicio>-<fin>.csv (q11), indices_enso de q06 (data/processed/e3/)
Salida: figures/e3/e3_A07_indices_base_fija.png

Uso: python3 scripts_e3/plotA07_indices_base_fija.py   (o bash rune3plot.sh A07)
     E3_GRUPO=40 python3 scripts_e3/plotA07_indices_base_fija.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig = figura_indices(["ONIfija", "ICENfija"], "Índices con base fija 1985-2014 (sin quitar el calentamiento)")
    guardar(fig, "A07_indices_base_fija")


if __name__ == "__main__":
    main()
