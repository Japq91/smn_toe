#!/usr/bin/env python3
"""plot03c -- figura e2_03c_sesgo_media_vs_variabilidad.png (seccion 3c de scripts_e2/plots_e2.ipynb).

Sesgo de la media vs sesgo de variabilidad en las cajas, con el mismo
formato que plot02d (un panel, Nino3.4 y Nino1+2 con distinto marcador).

Entrada: sesgo_tsm_ref<ref>.nc (p03), variabilidad_tsm_ref<ref>.nc (p04)
Salida: figures/e2/e2_03c_sesgo_media_vs_variabilidad.png

Uso: python3 scripts_e2/plot03c_sesgo_media_vs_variabilidad.py   (o bash rune2plot.sh 03c 03c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    sesgo_caja, var_caja = cargar_sesgo_caja(), cargar_var_caja()
    cmap, norm, ticks = cmap_modelos(continua=True, nombre="turbo")
    col = cmap(norm([int(n[1:]) for n in sesgo_caja.index]))   # color del modelo (barra 1..40)
    fig, ax = plt.subplots(figsize=(5, 4), layout="constrained")
    for caja, mk in zip(CAJAS, ["o", "s"]):
        c = NOM_CAJA[caja]
        ax.scatter(sesgo_caja[c], var_caja.loc[sesgo_caja.index, c], marker=mk, s=30, facecolor="none",
                   edgecolor=col, lw=.9)
        ax.scatter([], [], marker=mk, s=30, facecolor="none", edgecolor="k", lw=.9, label=c)   # solo leyenda
    ax.axhline(0, color="k", lw=0.5, ls="--")
    ax.axvline(0, color="k", lw=0.5, ls="--")
    ax.set_xlabel("sesgo medio anual [°C]")
    ax.set_ylabel("Δσ de la anomalía [%]")
    ax.legend(frameon=True)
    titulo_panel(ax, None, "Media vs variabilidad interanual")
    barra_modelos(fig, ax, cmap, norm, ticks[::2], pad=0.02)
    guardar(fig, "03c_sesgo_media_vs_variabilidad")


if __name__ == "__main__":
    main()
