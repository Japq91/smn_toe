#!/usr/bin/env python3
"""plot04c -- figura e2_04c_asimetria_oni_icen.png (seccion 4c de scripts_e2/plots_e2.ipynb).

Asimetria ICEN vs ONI.

Entrada: indices_enso_<y0>-<y1>.csv (p01) + OBS
Salida: figures/e2/e2_04c_asimetria_oni_icen.png

Uso: python3 scripts_e2/plot04c_asimetria_oni_icen.py   (o bash rune2plot.sh 04c 04c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    est = cargar_est()
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(est.loc[numbers, "skew_ONI"], est.loc[numbers, "skew_ICEN"], marker="o", s=30, c="steelblue", edgecolor="k", lw=0.4)
    for n in numbers:
        ax.annotate(n[1:], (est.loc[n, "skew_ONI"], est.loc[n, "skew_ICEN"]), fontsize=6, xytext=(2, 2), textcoords="offset points")
    ax.scatter(est.loc["OBS", "skew_ONI"], est.loc["OBS", "skew_ICEN"], marker="D", s=50, c=".2", label="ERSSTv5")
    ax.axhline(0, color="0.5", lw=0.5)
    ax.axvline(0, color="0.5", lw=0.5)
    ax.set_xlabel("asimetría ONI (Niño3.4)")
    ax.set_ylabel("asimetría ICEN (Niño1+2)")
    ax.legend(frameon=True)
    plt.tight_layout()
    guardar(fig, "04c_asimetria_oni_icen")


if __name__ == "__main__":
    main()
