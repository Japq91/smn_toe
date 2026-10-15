#!/usr/bin/env python3
"""plot06 -- figura e2_02d_sesgo_vs_amplitud.png (seccion 2d de scripts_e2/plots_e2.ipynb).

Sesgo de la media vs amplitud del ciclo anual (usa la tabla de la seccion 2c).

Entrada: climatologia_<caja>_<ref>.csv (p02) + ERSSTv5
Salida: figures/e2/e2_02d_sesgo_vs_amplitud.png

Uso: python3 scripts_e2/plot06_sesgo_vs_amplitud.py   (o bash rune2plot.sh 06 06)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    tab_clim = cargar_tab_clim()
    fig, ax = plt.subplots(figsize=(6, 5))
    for caja, mk in zip(CAJAS, ["o", "s"]):
        t = tab_clim[NOM_CAJA[caja]].drop(index="OBS")
        ax.scatter(t["sesgo (°C)"], t["amplitud / OBS"], marker=mk, s=28, edgecolor="k", lw=0.4, label=NOM_CAJA[caja])
    ax.axhline(1, color="k", lw=0.6, ls="--")
    ax.axvline(0, color="k", lw=0.6, ls="--")
    ax.set_xlabel("sesgo medio anual (°C)")
    ax.set_ylabel("amplitud del ciclo anual / ERSSTv5")
    ax.legend(frameon=True)
    ax.set_title("Media vs amplitud del ciclo anual")
    plt.tight_layout()
    guardar(fig, "02d_sesgo_vs_amplitud")


if __name__ == "__main__":
    main()
