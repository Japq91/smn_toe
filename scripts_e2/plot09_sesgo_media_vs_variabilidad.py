#!/usr/bin/env python3
"""plot09 -- figura e2_03c_sesgo_media_vs_variabilidad.png (seccion 3c de scripts_e2/plots_e2.ipynb).

Sesgo de media vs sesgo de variabilidad en las cajas.

Entrada: sesgo_tsm_ref<ref>.nc (p03), variabilidad_tsm_ref<ref>.nc (p04)
Salida: figures/e2/e2_03c_sesgo_media_vs_variabilidad.png

Uso: python3 scripts_e2/plot09_sesgo_media_vs_variabilidad.py   (o bash rune2plot.sh 09 09)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    sesgo_caja, var_caja = cargar_sesgo_caja(), cargar_var_caja()
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, caja in zip(axs, ["Niño3.4", "Niño1+2"]):
        ax.scatter(sesgo_caja[caja], var_caja[caja], s=30, edgecolor="k", lw=0.4)
        for n in var_caja.index:
            ax.annotate(n[1:], (sesgo_caja.loc[n, caja], var_caja.loc[n, caja]), fontsize=6, xytext=(2, 2), textcoords="offset points")
        ax.axhline(0, color="k", lw=0.6, ls="--")
        ax.axvline(0, color="k", lw=0.6, ls="--")
        ax.set_xlabel("sesgo de la media (°C)")
        ax.set_title(caja)
    axs[0].set_ylabel("Δσ de la anomalía (%)")
    plt.tight_layout()
    guardar(fig, "03c_sesgo_media_vs_variabilidad")


if __name__ == "__main__":
    main()
