#!/usr/bin/env python3
"""plot02b -- figura e2_02b_sesgo_mensual_climatologia.png (seccion 2b de scripts_e2/plots_e2.ipynb).

Sesgo mensual de la climatologia (modelo - ERSSTv5), por caja.

Entrada: climatologia_<caja>_<ref>.csv (p02) + ERSSTv5
Salida: figures/e2/e2_02b_sesgo_mensual_climatologia.png

Uso: python3 scripts_e2/plot02b_sesgo_mensual_climatologia.py   (o bash rune2plot.sh 02b 02b)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    clim, clim_obs = cargar_clim()
    n_bins = 11                              # 11 franjas de color
    levels = np.linspace(-4, 4, n_bins + 1)  # 12 bordes
    cmap = plt.get_cmap("RdBu_r", n_bins)    # 11 colores, uno por franja
    norm = mcolors.BoundaryNorm(levels, ncolors=n_bins, clip=False)

    fig, axs = plt.subplots(2, 1, figsize=(12, 6))
    for ax, caja in zip(axs, CAJAS):
        d = clim[caja] - clim_obs[caja]
        d = d.loc[d.mean(axis=1).sort_values().index].T
        im = ax.imshow(d.values, cmap=cmap, norm=norm, aspect="auto")
        ax.set_yticks(range(12))
        ax.set_yticklabels(MESES)
        ax.set_xticks(range(len(d.columns)))
        ax.set_xticklabels([etiqueta[n] for n in d.columns], fontsize=9, rotation=90)
        ax.set_title(f"{NOM_CAJA[caja]}: modelo - ERSSTv5")

    fig.subplots_adjust(hspace=0.4)

    fig.colorbar(
        im, ax=axs, shrink=0.5, label="°C",
        ticks=levels, extend="both", spacing="uniform",
    )
    guardar(fig, "02b_sesgo_mensual_climatologia")


if __name__ == "__main__":
    main()
