#!/usr/bin/env python3
"""plot09b -- figura e2_09b_heatmap_skill.png (seccion 9b de scripts_e2/plots_e2.ipynb).

Mapa de calor de S (modelos x componentes) y concordancia entre indices, ventanas ±12, ±15 y ±18 meses.

Entrada: skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_09b_heatmap_skill.png

Uso: python3 scripts_e2/plot09b_heatmap_skill.py   (o bash rune2plot.sh 09b 09b)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    skv, o = cargar_skv(), orden_s_final()
    lim_s = np.round(np.arange(0.3, 1.001, 0.05), 2)
    lim_r = np.round(np.arange(-1, 1.001, 0.2), 1)
    cmap_s, norm_s = discreta("viridis", lim_s)
    cmap_r, norm_r = discreta("RdBu_r", lim_r)
    cols = ["S_nino34", "S_nino12", "S_ONI", "S_RONI", "S_ICEN", "S_final"]
    fig, axs = plt.subplots(2, len(VENTANAS), figsize=(7 * len(VENTANAS), 16), gridspec_kw=dict(height_ratios=[2.4, 1]),
                            layout="constrained")
    for col, v in enumerate(VENTANAS):
        s = skv[v].reindex(o.index)
        ax = axs[0, col]
        im = ax.imshow(s[cols].values, cmap=cmap_s, norm=norm_s, aspect="auto")
        for (r_, c_), val in np.ndenumerate(s[cols].values):
            ax.text(c_, r_, f"{val:.2f}", ha="center", va="center", fontsize=5.5, color="w" if val < 0.7 else "k")
        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=45, ha="right")
        ax.set_yticks(range(len(s)))
        ax.set_yticklabels([etiqueta[n] for n in s.index] if col == 0 else [], fontsize=7)
        ax.axvline(1.5, color="w", lw=2)
        titulo_panel(ax, LETRAS[col], f"S -- compuesto ±{v} m (orden: S_final ±{VENTANA} m)")

        rho = skv[v][cols].corr(method="spearman")
        ax2 = axs[1, col]
        im2 = ax2.imshow(rho, cmap=cmap_r, norm=norm_r)
        for (r_, c_), val in np.ndenumerate(rho.values):
            ax2.text(c_, r_, f"{val:.2f}", ha="center", va="center", fontsize=8)
        ax2.set_xticks(range(len(cols)))
        ax2.set_xticklabels(cols, rotation=45, ha="right")
        ax2.set_yticks(range(len(cols)))
        ax2.set_yticklabels(cols)
        titulo_panel(ax2, LETRAS[len(VENTANAS) + col], f"Spearman ρ entre rankings -- ±{v} m")
    barra(fig, im, axs[0], "S", lim_s, cada=2, extend="min")
    barra(fig, im2, axs[1], "Spearman ρ", lim_r)
    guardar(fig, "09b_heatmap_skill")


if __name__ == "__main__":
    main()
