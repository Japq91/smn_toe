#!/usr/bin/env python3
"""plot07c -- figura e2_07c_magnitud_eventos.png (seccion 7c de scripts_e2/plots_e2.ipynb).

Magnitud del pico de cada evento (boxplot por dataset, ordenado por mediana).

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07)
Salida: figures/e2/e2_07c_magnitud_eventos.png

Uso: python3 scripts_e2/plot07c_magnitud_eventos.py   (o bash rune2plot.sh 07c 07c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    ev = cargar_eventos()
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=False)
    for ax, letra, i in zip(axs, LETRAS, INDICES):
        g = ev[i].groupby("number")["magnitud_pico"]
        orden = g.median().sort_values().index.tolist()
        data = [g.get_group(n).values for n in orden]
        bp = ax.boxplot(data, patch_artist=True, widths=0.7, showfliers=True, flierprops=dict(ms=2))
        for patch, n in zip(bp["boxes"], orden):
            patch.set_facecolor("k" if n == "OBS" else COL_IDX[i])
            patch.set_alpha(0.9 if n == "OBS" else 0.6)
        ax.axhline(g.get_group("OBS").median(), color="k", ls="--", lw=0.8)
        ax.set_xticks(range(1, len(orden) + 1))
        ax.set_xticklabels([etiqueta.get(n, "ERSSTv5") for n in orden], rotation=90, fontsize=8)
        ax.set_ylabel(f"pico [°C]")
        titulo_panel(ax, letra, i)
    plt.tight_layout()
    fig.subplots_adjust(hspace=0.7)
    guardar(fig, "07c_magnitud_eventos")


if __name__ == "__main__":
    main()
