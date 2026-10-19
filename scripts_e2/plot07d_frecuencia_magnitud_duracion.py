#!/usr/bin/env python3
"""plot07d -- figura e2_07d_frecuencia_magnitud_duracion.png (seccion 7d de scripts_e2/plots_e2.ipynb).

Frecuencia vs magnitud vs duracion de los eventos.

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07), indices_enso_<y0>-<y1>.csv (p01)
Salida: figures/e2/e2_07d_frecuencia_magnitud_duracion.png

Uso: python3 scripts_e2/plot07d_frecuencia_magnitud_duracion.py   (o bash rune2plot.sh 07d 07d)
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import BoundaryNorm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


# color de ERSSTv5 por indice: cruce de lineas en su panel y raya en la barra
COL_OBS = {"ONI": "b", "RONI": "r", "ICEN": "k"}


def main():
    ev, siglos = cargar_eventos(), cargar_siglos()

    # --- grupos (una sola vez) ---
    gs = {}
    for i in INDICES:
        g = ev[i].groupby("number").agg(n=("magnitud_pico", "size"),
                                        mag=("magnitud_pico", "mean"),
                                        dur=("duracion_meses", "mean"))
        g["freq"] = g["n"] / [siglos[(n, i)] for n in g.index]
        gs[i] = g

    # --- escala discreta 4..24 cada 2, con extend both ---
    bounds = np.arange(5, 25, 2)
    N = len(bounds) - 1
    cmap = plt.get_cmap("viridis", N)
    norm = BoundaryNorm(bounds, cmap.N)

    fig, axs = plt.subplots(1, 3, figsize=(12, 3.2), sharey='row', layout="constrained")
    for ax, letra, i in zip(axs, LETRAS, INDICES):
        g = gs[i]
        m, o = g.drop(index="OBS"), g.loc["OBS"]
        sc = ax.scatter(m["freq"], m["mag"], s=m["dur"] * 6, c=m["dur"],
                        cmap=cmap, norm=norm, alpha=0.7,
                        edgecolor="k", lw=0.4)
        for n in m.index:
            s_val = m.loc[n, "dur"] * 6
            fs = float(np.clip(np.sqrt(s_val) * 0.75, 4, 10))
            rgba = cmap(norm(m.loc[n, "dur"]))
            vis = 0.6 * np.asarray(rgba[:3]) + 0.4 * np.array([1., 1., 1.])
            lum = 0.299 * vis[0] + 0.587 * vis[1] + 0.114 * vis[2]
            txt_color = "white" if lum < 0.55 else "black"
            ax.annotate(n[1:], (m.loc[n, "freq"], m.loc[n, "mag"]),
                        fontsize=fs, ha="center", va="center", color=txt_color)

        # OBS como cruce de lineas (vertical + horizontal)
        ax.axvline(o["freq"], color=COL_OBS[i], lw=0.9, ls="-", zorder=2, alpha=0.8)
        ax.axhline(o["mag"],  color=COL_OBS[i], lw=0.9, ls="-", zorder=2, alpha=0.8)

        ax.set_xlabel("frecuencia [eventos/siglo]")
        ax.set_ylabel("magnitud pico media [°C]")
        titulo_panel(ax, letra, i)

    # una sola barra para los tres paneles (misma escala), 80% del alto del panel;
    # lineas: duracion media observada de cada indice, con el color de su panel
    cb = fig.colorbar(sc, cax=barra_inset(axs[-1], 0.8, 0.04, 0.05), label="duración media [meses]",
                      ticks=bounds, extend="both", spacing="uniform")
    for i in INDICES:
        # raya desplazada: mitad dentro de la barra y mitad fuera, a la izquierda
        cb.ax.plot([-0.5, 0.5], [gs[i].loc["OBS", "dur"]] * 2, color=COL_OBS[i], lw=1.6,
                   transform=cb.ax.get_yaxis_transform(), clip_on=False)
    guardar(fig, "07d_frecuencia_magnitud_duracion")


if __name__ == "__main__":
    main()