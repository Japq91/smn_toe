#!/usr/bin/env python3
"""plot26 -- figura e2_09a_ranking_skill.png (seccion 9a de scripts_e2/plots_e2.ipynb).

Ranking por S_final, con el S de cada indice, ventanas ±12, ±15 y ±18 meses.

Entrada: skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_09a_ranking_skill.png

Uso: python3 scripts_e2/plot26_ranking_skill.py   (o bash rune2plot.sh 26 26)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    skv = cargar_skv()
    fig, axs = plt.subplots(len(VENTANAS), 1, figsize=(14, 4.8 * len(VENTANAS)))
    for ax, v in zip(axs, VENTANAS):
        ov = skv[v].sort_values("S_final", ascending=False)
        x = np.arange(len(ov))
        ax.bar(x, ov["S_final"], color=np.where(ov["seleccionado"], "0.45", "0.82"), width=0.8,
               label="S_final (oscuro = seleccionado, ≥ p75)")
        for k, i in enumerate(INDICES):
            ax.plot(x + (k - 1) * 0.22, ov[f"S_{i}"], "o", ms=4, color=COL_IDX[i], label=f"S_{i}")
        ax.plot(x, ov["S_nino34"], "_", ms=8, color="k", label="S_nino34 (serie completa, ref.)")
        for q, ls in [(0.75, "--"), (0.5, ":")]:
            ax.axhline(ov["S_final"].quantile(q), color="firebrick", ls=ls, lw=0.8, label=f"p{int(q*100)} de S_final")
        ax.set_xticks(x)
        ax.set_xticklabels([etiqueta[n] for n in ov.index], rotation=90, fontsize=7)
        ax.set_ylabel("S")
        ax.set_ylim(0, 1.02)
        ax.set_title(f"Score de habilidad de Taylor por modelo (ordenado por S_final) -- compuesto ±{v} m")
    axs[0].legend(ncol=4, fontsize=7, frameon=False, loc="lower left")
    plt.tight_layout()
    guardar(fig, "09a_ranking_skill")


if __name__ == "__main__":
    main()
