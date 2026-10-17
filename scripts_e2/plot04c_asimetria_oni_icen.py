#!/usr/bin/env python3
"""plot04c -- figura e2_04c_asimetria_oni_icen.png (seccion 4c de scripts_e2/plots_e2.ipynb).

ICEN vs ONI en dos paneles: (a) asimetria y (b) curtosis (exceso), con el
mismo formato que plot02d. Las lineas punteadas marcan el valor de
ERSSTv5 (el rombo), como la referencia perfecta en 02d.

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
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for ax, letra, (stat, nom) in zip(axs, LETRAS, [("skew", "asimetría"), ("kurt", "curtosis (exceso)")]):
        x, y = f"{stat}_ONI", f"{stat}_ICEN"
        ax.scatter(est.loc[numbers, x], est.loc[numbers, y], marker="o", s=150, color="tab:blue", alpha=0.6,
                   edgecolor="k", lw=0.4, label="40 modelos")
        for n in numbers:   # numero del modelo dentro del circulo
            ax.annotate(n[1:], (est.loc[n, x], est.loc[n, y]), fontsize=6, ha="center", va="center")
        ax.scatter(est.loc["OBS", x], est.loc["OBS", y], marker="D", s=50, c="k", label="ERSSTv5", zorder=3)
        ax.axhline(est.loc["OBS", y], color="k", lw=0.6, ls="--")
        ax.axvline(est.loc["OBS", x], color="k", lw=0.6, ls="--")
        ax.set_xlabel(f"{nom} ONI (Niño3.4)")
        ax.set_ylabel(f"{nom} ICEN (Niño1+2)")
        ax.legend(frameon=True)
        titulo_panel(ax, letra, f"{nom.split(' (')[0].capitalize()}: ICEN vs ONI")
    plt.tight_layout()
    guardar(fig, "04c_asimetria_oni_icen")


if __name__ == "__main__":
    main()
