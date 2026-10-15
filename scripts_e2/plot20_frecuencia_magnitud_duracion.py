#!/usr/bin/env python3
"""plot20 -- figura e2_07d_frecuencia_magnitud_duracion.png (seccion 7d de scripts_e2/plots_e2.ipynb).

Frecuencia vs magnitud vs duracion de los eventos.

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07), indices_enso_<y0>-<y1>.csv (p01)
Salida: figures/e2/e2_07d_frecuencia_magnitud_duracion.png

Uso: python3 scripts_e2/plot20_frecuencia_magnitud_duracion.py   (o bash rune2plot.sh 20 20)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    ev, siglos = cargar_eventos(), cargar_siglos()
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, i in zip(axs, INDICES):
        g = ev[i].groupby("number").agg(n=("magnitud_pico", "size"), mag=("magnitud_pico", "mean"), dur=("duracion_meses", "mean"))
        g["freq"] = g["n"] / [siglos[(n, i)] for n in g.index]
        m, o = g.drop(index="OBS"), g.loc["OBS"]
        ax.scatter(m["freq"], m["mag"], s=m["dur"] * 6, c=COL_IDX[i], alpha=0.6, edgecolor="k", lw=0.4)
        for n in m.index:
            ax.annotate(n[1:], (m.loc[n, "freq"], m.loc[n, "mag"]), fontsize=6, xytext=(3, 3), textcoords="offset points")
        ax.scatter(o["freq"], o["mag"], marker="D", s=50, c="k", zorder=4, label=f"ERSSTv5 (dur. {o['dur']:.1f} m)")
        ax.set_xlabel("eventos / siglo")
        ax.set_ylabel("magnitud pico media (°C)")
        ax.set_title(i)
        ax.legend(frameon=True, fontsize=8)
    plt.tight_layout()
    guardar(fig, "07d_frecuencia_magnitud_duracion")


if __name__ == "__main__":
    main()
