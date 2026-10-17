#!/usr/bin/env python3
"""plot08c -- figura e2_08c_compuesto_r_sigma.png (seccion 8c de scripts_e2/plots_e2.ipynb).

Zoom del Taylor compuesto (r vs σ normalizado), ventanas ±12, ±15 y ±18 meses.

Entrada: taylor_compuesto_<INDICE>_vent<V>m_<y0>-<y1>.csv (p08), skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_08c_compuesto_r_sigma.png

Uso: python3 scripts_e2/plot08c_compuesto_r_sigma.py   (o bash rune2plot.sh 08c 08c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    tcv, skv = cargar_tcv(), cargar_skv()
    lim = np.linspace(0.37, 1.0, 22)   # mismas 21 clases que 08b
    cmap, norm = discreta("viridis", lim)
    fig, axs = plt.subplots(len(VENTANAS), 3, figsize=(12, 3.5 * len(VENTANAS)),
                            sharex=True, sharey=True, layout="constrained")
    sc_last = None
    letras = iter(LETRAS)
    for fila, v in enumerate(VENTANAS):
        for ax, i in zip(axs[fila], INDICES):
            m = tcv[v][i].drop(index="OBS")
            sc = ax.scatter(m["r"], m["sigma_norm"],
                            c=skv[v][f"S_{i}"].reindex(m.index), cmap=cmap, norm=norm, alpha=0.7,
                            s=20, edgecolor="k", lw=0.4)
            sc_last = sc
            for n in m.index:
                ax.annotate(n[1:], (m.loc[n, "r"], m.loc[n, "sigma_norm"]),
                            fontsize=6, xytext=(2, 2), textcoords="offset points")
            ax.scatter(1, 1, marker="D", s=30, alpha=0.8,c="k")
            ax.axhline(1, color="k", lw=0.5, ls="--")
            titulo_panel(ax, next(letras), f"{i} -- ±{v} m")
            if fila == len(VENTANAS) - 1:
                ax.set_xlabel("r (forma del compuesto)")
        axs[fila, 0].set_ylabel("σ normalizado")

    barra(fig, sc_last, axs, "skill score (S)", lim, cada=3, pad=0.02)
    guardar(fig, "08c_compuesto_r_sigma")


if __name__ == "__main__":
    main()
