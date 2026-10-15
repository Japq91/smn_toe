#!/usr/bin/env python3
"""plot06b -- figura e2_06b_correlacion_por_modelo.png (seccion 6b de scripts_e2/plots_e2.ipynb).

Correlacion por modelo (Pacifico tropical 120E-70W), un mapa por modelo.

Entrada: correlacion_tsm_ref<ref>.nc (p06)
Salida: figures/e2/e2_06b_correlacion_por_modelo.png

Uso: python3 scripts_e2/plot06b_correlacion_por_modelo.py   (o bash rune2plot.sh 06b 06b)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    corr, pval = cargar_corr()
    fig = multiples(corr, "RdBu_r", mcolors.TwoSlopeNorm(0, -0.8, 0.8), "Correlación modelo vs ERSSTv5 (punteado: p<0.05)", "r",
                    punteado=pval < 0.05)
    guardar(fig, "06b_correlacion_por_modelo")


if __name__ == "__main__":
    main()
