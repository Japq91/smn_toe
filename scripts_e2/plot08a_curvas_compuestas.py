#!/usr/bin/env python3
"""plot08a -- figura e2_08a_curvas_compuestas.png (seccion 8a de scripts_e2/plots_e2.ipynb).

Curvas compuestas (evento tipico) centradas en el pico, una fila por indice,
con la ventana de ±18 meses; lineas verticales en -/+12, 15 y 18 meses.

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07), indices_enso_<y0>-<y1>.csv (p01)
Salida: figures/e2/e2_08a_curvas_compuestas.png

Uso: python3 scripts_e2/plot08a_curvas_compuestas.py   (o bash rune2plot.sh 08a 08a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    curvas, _ = cargar_curvas()
    v = max(VENTANAS)  # la de 18 meses contiene a las otras dos
    t = np.arange(-v, v + 1)
    fig, axs = plt.subplots(len(INDICES), 1, figsize=(10, 9), sharex=True)
    for fila, (ax, i) in enumerate(zip(axs, INDICES)):
        M = np.vstack([curvas[v][i][n] for n in numbers if n in curvas[v][i]])
        for w in VENTANAS:  # limites de las tres ventanas
            for x in (-w, w):
                ax.axvline(x, color="0.55", lw=0.8, ls="--", zorder=0)
            ax.annotate(f"{w}m", (-w, 1), xycoords=("data", "axes fraction"), xytext=(2, -3),
                        textcoords="offset points", rotation=90, ha="left", va="top",
                        fontsize=8, color="0.4")
        ax.plot(t, M.T, color=COL_IDX[i], alpha=0.2, lw=0.6)
        ax.plot(t, M.mean(axis=0), color=COL_IDX[i], lw=2, label="media modelos")
        ax.plot(t, curvas[v][i]["OBS"], color="k", lw=2.2, label="ERSSTv5")
        ax.axvline(0, color="0.4", lw=0.6)
        ax.axhline(0, color="0.4", lw=0.6)
        ax.set_xlim(-v, v)
        titulo_panel(ax, LETRAS[fila], f"{i}: ventanas")
        ax.set_ylabel(f"{i} [°C]")
    axs[-1].set_xlabel("tiempo relativo al pico [meses]")
    axs[0].legend(frameon=False, fontsize=8, loc="upper right")
    plt.tight_layout()
    guardar(fig, "08a_curvas_compuestas")

if __name__ == "__main__":
    main()
