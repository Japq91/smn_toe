#!/usr/bin/env python3
"""plot11 -- figura e2_04b_estadisticos_indices.png (seccion 4b de scripts_e2/plots_e2.ipynb).

σ, asimetria (skewness) y curtosis de cada indice por modelo.

Entrada: indices_enso_<y0>-<y1>.csv (p01) + OBS
Salida: figures/e2/e2_04b_estadisticos_indices.png

Uso: python3 scripts_e2/plot11_estadisticos_indices.py   (o bash rune2plot.sh 11 11)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    est = cargar_est()
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    x = np.arange(len(numbers))
    for ax, stat, lab in zip(axs, ["σ", "skew", "kurt"], ["σ (°C)", "asimetría", "curtosis (exceso)"]):
        for k, ind in enumerate(INDICES):
            ax.plot(x + (k - 1) * 0.22, est.loc[numbers, f"{stat}_{ind}"], M_IDX[ind], ms=4, color=COL_IDX[ind], label=ind)
            ax.axhline(est.loc["OBS", f"{stat}_{ind}"], color=COL_IDX[ind], ls="--", lw=0.9)
        ax.axhline(0, color="0.3", lw=0.4)
        ax.set_ylabel(lab)
        ax.grid(axis="x", color="0.93")
    axs[0].legend(ncol=3, frameon=False, fontsize=8, title="(-- = ERSSTv5)", title_fontsize=8)
    axs[-1].set_xticks(x)
    axs[-1].set_xticklabels([etiqueta[n] for n in numbers], rotation=90, fontsize=7)
    fig.suptitle("σ, asimetría y curtosis de cada índice por modelo")
    plt.tight_layout()
    guardar(fig, "04b_estadisticos_indices")


if __name__ == "__main__":
    main()
