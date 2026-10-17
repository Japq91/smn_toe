#!/usr/bin/env python3
"""plot05a -- figura e2_05a_taylor_serie_completa.png (seccion 5 de scripts_e2/plots_e2.ipynb).

Taylor sobre la anomalia mensual completa 1981-2014 por caja (p05), en
semicirculo porque varios modelos tienen r < 0. El color es el S_final de
p09 con la ventana +-12 m del compuesto; no cambia los datos del diagrama.

Entrada: taylor_<caja>_ref<ref>.csv (p05), skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_05a_taylor_serie_completa.png

Uso: python3 scripts_e2/plot05a_taylor_serie_completa.py   (o bash rune2plot.sh 05a 05a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    tay, skv = cargar_tay(), cargar_skv()
    v = VENTANAS[0]  # S_final del resultado principal (compuesto +-12 m)

    # Barra discreta: 21 clases de 0.025 entre 0.475 y 1 (S_final va de 0.53 a 0.98)
    limites = np.linspace(0.475, 1.0, 22)
    cmap = plt.get_cmap("viridis", len(limites) - 1)
    norm = mcolors.BoundaryNorm(limites, cmap.N)

    fig, axs = plt.subplots(1, 2, figsize=(15, 5), layout="constrained")
    for ax, letra, (c, t) in zip(axs, "ab", tay.items()):
        sc = taylor(
            ax, t,
            f"{NOM_CAJA[c]}: anomalía mensual {REF}", letra=letra,
            color=skv[v]["S_final"].reindex(t.drop(index="OBS").index),
            semicirculo=True, cmap=cmap, norm=norm,
        )

    axs[0].legend(loc="upper left", frameon=False)
    cb = fig.colorbar(sc, ax=axs, label="S_final", ticks=limites[::4])
    cb.ax.tick_params(labelsize=8)
    guardar(fig, "05a_taylor_serie_completa")


if __name__ == "__main__":
    main()
