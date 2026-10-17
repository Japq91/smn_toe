#!/usr/bin/env python3
"""plot04a -- figura e2_04a_indices_envolvente.png (seccion 4a de scripts_e2/plots_e2.ipynb).

ONI, RONI e ICEN -- envolvente multimodelo vs OBS.

Entrada: indices_enso_<y0>-<y1>.csv (p01) + OBS
Salida: figures/e2/e2_04a_indices_envolvente.png

Uso: python3 scripts_e2/plot04a_indices_envolvente.py   (o bash rune2plot.sh 04a 04a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    df = cargar_indices()
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    for ax, letra, ind in zip(axs, LETRAS, INDICES):
        mods = df[[f"{n}_{ind}" for n in numbers]]
        ax.fill_between(df.index, mods.quantile(0.1, axis=1), mods.quantile(0.9, axis=1),
                        color="0.8", lw=0, label="p10-p90 modelos")
        ax.plot(df.index, mods.median(axis=1), color=COL_IDX[ind], lw=0.9, label="mediana modelos")
        ax.plot(df.index, df[f"OBS_{ind}"], color="k", lw=1.1, label="ERSSTv5")
        umbral = 0.5   # ONI/RONI (NOAA CPC) e ICEN (ENFEN 01-2024)
        ax.axhline(umbral, color="firebrick", ls="--", lw=0.7)
        ax.axhline(-umbral, color="steelblue", ls="--", lw=0.7)
        ax.axhline(0, color="0.3", lw=0.4)
        ax.set_ylabel(f"{ind} [°C]")
        titulo_panel(ax, letra, ind)
    axs[0].legend(loc="upper left", ncol=3, frameon=False, fontsize=8)
    axs[-1].set_xlabel("Año")
    fig.suptitle("Índices ENOS -- 40 modelos CMIP6 vs ERSSTv5")
    plt.tight_layout()
    guardar(fig, "04a_indices_envolvente")


if __name__ == "__main__":
    main()
