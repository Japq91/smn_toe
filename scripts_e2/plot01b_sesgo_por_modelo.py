#!/usr/bin/env python3
"""plot01b -- figura e2_01b_sesgo_por_modelo.png (seccion 1b de scripts_e2/plots_e2.ipynb).

Sesgo por modelo (Pacifico tropical 120E-70W), un mapa por modelo.

Entrada: sesgo_tsm_ref<ref>.nc (p03)
Salida: figures/e2/e2_01b_sesgo_por_modelo.png

Uso: python3 scripts_e2/plot01b_sesgo_por_modelo.py   (o bash rune2plot.sh 01b 01b)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    bias = cargar_bias()
    fig = multiples(bias, "RdBu_r", mcolors.TwoSlopeNorm(0, -4, 4), f"Sesgo de TSM, modelo - ERSSTv5 (ref {REF})", "[°C]")
    guardar(fig, "01b_sesgo_por_modelo")


if __name__ == "__main__":
    main()
