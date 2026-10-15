#!/usr/bin/env python3
"""plot05a -- figura e2_05a_taylor_serie_completa.png (seccion 5 de scripts_e2/plots_e2.ipynb).

Taylor sobre la serie completa por caja (color = S_final de p09, una fila por ventana).

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
    vmin_sf = min(skv[v]["S_final"].min() for v in VENTANAS)
    fig, axs = plt.subplots(len(VENTANAS), 2, figsize=(13, 6 * len(VENTANAS)))
    for fila, v in enumerate(VENTANAS):
        for ax, (c, t) in zip(axs[fila], tay.items()):
            sc = taylor(ax, t, f"{NOM_CAJA[c]} -- color: S_final ±{v} m",
                        color=skv[v]["S_final"].reindex(t.drop(index="OBS").index))
            sc.set_clim(vmin_sf, 1)
    axs[0, 0].legend(loc="upper right", frameon=False)
    fig.colorbar(sc, ax=axs, shrink=0.4, label="S_final (p09)")
    guardar(fig, "05a_taylor_serie_completa")


if __name__ == "__main__":
    main()
