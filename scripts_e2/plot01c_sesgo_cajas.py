#!/usr/bin/env python3
"""plot01c -- figura e2_01c_sesgo_cajas.png (seccion 1c de scripts_e2/plots_e2.ipynb).

Sesgo medio en las cajas Niño3.4 y Niño1+2, por modelo.

Entrada: sesgo_tsm_ref<ref>.nc (p03)
Salida: figures/e2/e2_01c_sesgo_cajas.png

Uso: python3 scripts_e2/plot01c_sesgo_cajas.py   (o bash rune2plot.sh 01c 01c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    sesgo_caja = cargar_sesgo_caja()
    fig, ax = plt.subplots(figsize=(13, 4))
    sesgo_caja.plot.bar(ax=ax, width=0.8, color=["steelblue", ".6"])
    ax.axhline(0, color="k", lw=0.8, alpha=.9)
    ax.set_xticklabels([etiqueta[n] for n in sesgo_caja.index], rotation=90, fontsize=9)
    ax.set_ylabel("sesgo [°C]")
    titulo_panel(ax, None, "Sesgo medio de TSM por Región")
    plt.tight_layout()
    guardar(fig, "01c_sesgo_cajas")


if __name__ == "__main__":
    main()
