#!/usr/bin/env python3
"""plot08b -- figura e2_08b_taylor_compuesto.png (seccion 8b de scripts_e2/plots_e2.ipynb).

Diagrama de Taylor del compuesto (color = S del indice, p09), ventanas ±12, ±15 y ±18 meses.

Entrada: taylor_compuesto_<INDICE>_vent<V>m_<y0>-<y1>.csv (p08), skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_08b_taylor_compuesto.png

Uso: python3 scripts_e2/plot08b_taylor_compuesto.py   (o bash rune2plot.sh 08b 08b)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    tcv, skv = cargar_tcv(), cargar_skv()
    rmax_c = max(1.6, max(float(np.ceil(tcv[v][i]["sigma_norm"].max() * 10) / 10) + 0.1 for v in VENTANAS for i in INDICES))

    # Barra discreta: 21 clases de 0.03 entre 0.37 y 1 (S va de 0.40 a 1.00 en las tres ventanas)
    limites = np.linspace(0.37, 1.0, 22)
    cmap = plt.get_cmap("viridis", len(limites) - 1)
    norm = mcolors.BoundaryNorm(limites, cmap.N)

    fig, axs = plt.subplots(len(VENTANAS), 3, figsize=(17, 6 * len(VENTANAS)), layout="constrained")
    letras = iter(LETRAS)
    for fila, v in enumerate(VENTANAS):
        for ax, i in zip(axs[fila], INDICES):
            mod = tcv[v][i].drop(index="OBS")
            sc = taylor(ax, tcv[v][i], f"{i} (compuesto ±{v} m)", letra=next(letras),
                        color=skv[v][f"S_{i}"].reindex(mod.index), rmax=rmax_c, cmap=cmap, norm=norm)
    axs[0, 0].legend(loc="upper right", frameon=True)
    cb = fig.colorbar(sc, ax=axs, label="S (Taylor 2001)", ticks=limites[::3])
    cb.ax.tick_params(labelsize=8)
    guardar(fig, "08b_taylor_compuesto")


if __name__ == "__main__":
    main()
