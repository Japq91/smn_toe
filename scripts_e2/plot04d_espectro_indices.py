#!/usr/bin/env python3
"""plot04d -- figura e2_04d_espectro_indices.png (seccion 4d de scripts_e2/plots_e2.ipynb).

Espectro de potencia (Welch) -- periodo dominante del ENOS.

Entrada: indices_enso_<y0>-<y1>.csv (p01) + OBS
Salida: figures/e2/e2_04d_espectro_indices.png

Uso: python3 scripts_e2/plot04d_espectro_indices.py   (o bash rune2plot.sh 04d 04d)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    df = cargar_indices()
    fig, axs = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, letra, ind in zip(axs, LETRAS, INDICES):
        specs = {}
        for n in numbers + ["OBS"]:
            s = df[f"{n}_{ind}"].dropna().values
            f, P = signal.welch(s - s.mean(), fs=12, nperseg=256, detrend="linear")   # f en ciclos/año
            specs[n] = P
        per = 1 / f[1:]
        M = np.vstack([specs[n][1:] for n in numbers])
        ax.fill_between(per, np.percentile(M, 10, axis=0), np.percentile(M, 90, axis=0), color="0.8", lw=0, label="p10-p90 modelos")
        ax.plot(per, np.median(M, axis=0), color=COL_IDX[ind], lw=1.2, label="mediana modelos")
        ax.plot(per, specs["OBS"][1:], color="k", lw=1.5, label="ERSSTv5")
        ax.axvspan(2, 7, color="gold", alpha=0.15)
        ax.set_xscale("log")
        ax.set_xlim(1, 20)
        ax.set_xticks([1, 2, 3, 5, 7, 10, 20])
        ax.set_xticklabels([1, 2, 3, 5, 7, 10, 20])
        ax.set_xlabel("período [años]")
        titulo_panel(ax, letra, ind)
    axs[0].set_ylabel("densidad espectral [°C²·año]")
    axs[0].legend(frameon=False, fontsize=8)
    plt.tight_layout()
    guardar(fig, "04d_espectro_indices")


if __name__ == "__main__":
    main()
