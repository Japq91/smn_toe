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


# --- estilos por indice (marcador, tamaño, color, borde) ---
ESTILOS = {
    "ICEN":  dict(marker="o", s=18, color=COL_IDX["ICEN"],  edgecolor="k", lw=0.3, alpha=.6),
    "ONI":  dict(marker="v", s=20, color=COL_IDX["ONI"],  edgecolor="k", lw=0.3, alpha=.6),
    "RONI": dict(marker="^", s=20, color=COL_IDX["RONI"], edgecolor="k", lw=0.3, alpha=.6),
}
ESTILO_DEF = dict(marker="D", s=18, color="0.4", edgecolor="k", lw=0.3)


def main():
    tcv, skv = cargar_tcv(), cargar_skv()
    tc = tcv[VENTANA]   # ventana principal
    VENTANAS_SENS = [v for v in VENTANAS if v != VENTANA]
    MET = ["r", "sigma_norm", "rmse_centrado", "S_final"]
    fig, axs = plt.subplots(len(VENTANAS_SENS), len(MET), figsize=(12, 2.7 * len(VENTANAS_SENS)),sharex='col')

    # --- rango simetrico por columna (metrica) ---
    rangos = {}
    for met in MET:
        vals = []
        for v in VENTANAS_SENS:
            if met == "S_final":
                vals.append(skv[VENTANA]["S_final"].values)
                vals.append(skv[v]["S_final"].values)
            else:
                for i in INDICES:
                    vals.append(tc[i].drop(index="OBS")[met].values)
                    vals.append(tcv[v][i].drop(index="OBS")[met].values)
        vals = np.concatenate(vals)
        lo, hi = np.nanmin(vals), np.nanmax(vals)
        margen = 0.05 * (hi - lo) if hi > lo else 0.1
        rangos[met] = (lo - margen, hi + margen)

    for fila, v in enumerate(VENTANAS_SENS):
        for ax, met in zip(axs[fila], MET):
            if met == "S_final":
                pares = [("S_final", skv[VENTANA]["S_final"], skv[v]["S_final"], "0.4")]
            else:
                pares = [(i, tc[i].drop(index="OBS")[met], tcv[v][i].drop(index="OBS")[met], COL_IDX[i]) for i in INDICES]
            for lab, a, b, col in pares:
                comun = a.index.intersection(b.index)
                estilo = ESTILOS.get(lab, ESTILO_DEF)
                ax.scatter(a[comun], b[comun], label=lab, **estilo)

            lo, hi = rangos[met]
            ax.plot([lo, hi], [lo, hi], "k--", lw=0.7)
            ax.set_xlim(lo, hi)
            ax.set_ylim(lo, hi)
            ax.set_aspect("equal", adjustable="box")

            titulo_panel(ax, LETRAS[fila * len(MET) + MET.index(met)], met)
            ax.set_xlabel(f"{met} -- ventana {VENTANA} m")
            ax.set_ylabel(f"{met} -- ventana {v} m")
    axs[0, 0].legend(frameon=False)
    plt.tight_layout()
    guardar(fig, "08d_sensibilidad_ventana")


if __name__ == "__main__":
    main()