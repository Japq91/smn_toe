#!/usr/bin/env python3
"""plot08c -- figuras e2_08c_compuesto_r_sigma_<V>m.png (seccion 8c de scripts_e2/plots_e2.ipynb).

Zoom del Taylor compuesto (r vs σ normalizado): una figura por ventana
(±12, ±15 y ±18 meses) con los tres indices. Ejes y colores comunes a las
tres figuras para poder compararlas.

Entrada: taylor_compuesto_<INDICE>_vent<V>m_<y0>-<y1>.csv (p08), skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_08c_compuesto_r_sigma_{12,15,18}m.png

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
    # limites comunes a las tres ventanas
    todo = pd.concat([tcv[v][i].drop(index="OBS") for v in VENTANAS for i in INDICES])
    xlim = (todo["r"].min() - 0.01, 1.005)
    ylim = (todo["sigma_norm"].min() - 0.05, todo["sigma_norm"].max() + 0.08)
    for v in VENTANAS:
        fig, axs = plt.subplots(1, len(INDICES), figsize=(12, 4), sharex=True, sharey=True,
                                layout="constrained")
        for ax, letra, i in zip(axs, LETRAS, INDICES):
            m = tcv[v][i].drop(index="OBS")
            sc = ax.scatter(m["r"], m["sigma_norm"],
                            c=skv[v][f"S_{i}"].reindex(m.index), cmap=cmap, norm=norm, alpha=0.7,
                            s=20, edgecolor="k", lw=0.4)
            for n in m.index:
                ax.annotate(n[1:], (m.loc[n, "r"], m.loc[n, "sigma_norm"]),
                            fontsize=6, xytext=(2, 2), textcoords="offset points")
            ax.scatter(1, 1, marker="D", s=30, alpha=0.8, c="k")
            ax.axhline(1, color="k", lw=0.5, ls="--")
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            titulo_panel(ax, letra, f"{i} -- ±{v} m")
            ax.set_xlabel("r (forma del compuesto)")
        axs[0].set_ylabel("σ normalizado")
        barra(fig, sc, axs[-1], "skill score (S)", lim, cada=3, alto=0.8, ancho=0.04, pad=0.04)
        guardar(fig, f"08c_compuesto_r_sigma_{v}m")

if __name__ == "__main__":
    main()
