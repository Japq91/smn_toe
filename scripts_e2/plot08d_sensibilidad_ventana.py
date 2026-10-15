#!/usr/bin/env python3
"""plot08d -- figura e2_08d_sensibilidad_ventana.png (seccion 8d de scripts_e2/plots_e2.ipynb).

Sensibilidad al ancho de ventana (12 vs 15 y 12 vs 18 meses).

Entrada: taylor_compuesto_<INDICE>_vent<V>m_<y0>-<y1>.csv (p08), skill_score_vent<V>m_<y0>-<y1>.csv (p09)
Salida: figures/e2/e2_08d_sensibilidad_ventana.png

Uso: python3 scripts_e2/plot08d_sensibilidad_ventana.py   (o bash rune2plot.sh 08d 08d)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    tcv, skv = cargar_tcv(), cargar_skv()
    tc = tcv[VENTANA]   # ventana principal
    VENTANAS_SENS = [v for v in VENTANAS if v != VENTANA]
    MET = ["r", "sigma_norm", "rmse_centrado", "S_final"]
    fig, axs = plt.subplots(len(VENTANAS_SENS), len(MET), figsize=(18, 4.3 * len(VENTANAS_SENS)))
    for fila, v in enumerate(VENTANAS_SENS):
        for ax, met in zip(axs[fila], MET):
            if met == "S_final":
                pares = [("S_final", skv[VENTANA]["S_final"], skv[v]["S_final"], "0.4")]
            else:
                pares = [(i, tc[i].drop(index="OBS")[met], tcv[v][i].drop(index="OBS")[met], COL_IDX[i]) for i in INDICES]
            for lab, a, b, col in pares:
                comun = a.index.intersection(b.index)
                ax.scatter(a[comun], b[comun], s=18, color=col, edgecolor="k", lw=0.3, label=lab)
            lo = min(ax.get_xlim()[0], ax.get_ylim()[0]); hi = max(ax.get_xlim()[1], ax.get_ylim()[1])
            ax.plot([lo, hi], [lo, hi], "k--", lw=0.7)
            ax.set_xlabel(f"{met} -- ventana {VENTANA} m")
            ax.set_ylabel(f"{met} -- ventana {v} m")
    axs[0, 0].legend(frameon=False)
    plt.tight_layout()
    guardar(fig, "08d_sensibilidad_ventana")


if __name__ == "__main__":
    main()
