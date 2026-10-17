#!/usr/bin/env python3
"""plot08a -- figura e2_08a_curvas_compuestas.png (seccion 8a de scripts_e2/plots_e2.ipynb).

Curvas compuestas (evento tipico) centradas en el pico, ventanas ±12, ±15 y ±18 meses.

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
    fig, axs = plt.subplots(len(INDICES), len(VENTANAS), figsize=(16, 9), sharey="row")
    for fila, i in enumerate(INDICES):
        for col, v in enumerate(VENTANAS):
            ax = axs[fila, col]
            t = np.arange(-v, v + 1)
            M = np.vstack([curvas[v][i][n] for n in numbers if n in curvas[v][i]])
            ax.axvspan(-12, 12, color="0.94", lw=0)
            ax.plot(t, M.T, color=COL_IDX[i], alpha=0.2, lw=0.6)
            ax.plot(t, M.mean(axis=0), color=COL_IDX[i], lw=2, label="media modelos")
            ax.plot(t, curvas[v][i]["OBS"], color="k", lw=2.2, label="ERSSTv5")
            ax.axvline(0, color="0.4", lw=0.6)
            ax.axhline(0, color="0.4", lw=0.6)
            ax.set_xlim(-max(VENTANAS), max(VENTANAS))
            titulo_panel(ax, LETRAS[fila * len(VENTANAS) + col], f"{i}: ventana ±{v} meses")
            if col == 0:
                ax.set_ylabel(f"{i} [°C]")
            if fila == len(INDICES) - 1:
                ax.set_xlabel("tiempo relativo al pico [meses]")
    axs[0, 0].legend(frameon=False, fontsize=8)
    plt.tight_layout()
    guardar(fig, "08a_curvas_compuestas")


if __name__ == "__main__":
    main()
