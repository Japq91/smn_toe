#!/usr/bin/env python3
"""plot03b -- figura e2_03b_variabilidad_por_modelo.png (seccion 3b de scripts_e2/plots_e2.ipynb).

Variabilidad por modelo (Pacifico tropical 120E-70W), un mapa por modelo.

Entrada: variabilidad_tsm_ref<ref>.nc (p04)
Salida: figures/e2/e2_03b_variabilidad_por_modelo.png

Uso: python3 scripts_e2/plot03b_variabilidad_por_modelo.py   (o bash rune2plot.sh 03b 03b)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    dvar = cargar_dvar()
    fig = multiples(dvar, "PuOr_r", LIM_D, "Diferencia de σ de la anomalía, modelo vs ERSSTv5 [%]", "[%]")
    guardar(fig, "03b_variabilidad_por_modelo")


if __name__ == "__main__":
    main()
