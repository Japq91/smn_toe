#!/usr/bin/env python3
"""plotA10 -- Figura A10 del informe E3: figures/e3/e3_A10_sensibilidad_conjuntos.png

Sensibilidad al conjunto de modelos: mediana y p10-p90 del cambio en P2 para los
conjuntos de 15, 40, 11 y 7 modelos, con SSP2-4.5 y SSP5-8.5. Relleno = significativo
(Wilcoxon + Holm, q10).

Entrada: resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_A10_sensibilidad_conjuntos.png

Uso: python3 scripts_e3/plotA10_sensibilidad_conjuntos.py   (o bash rune3plot.sh A10)
     E3_GRUPO=40 python3 scripts_e3/plotA10_sensibilidad_conjuntos.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    per_sintesis = "P2"
    escs = ESCS_TDR
    ne = len(escs)
    variables = [("delta", "nino34", "ΔTSM Niño 3.4 [°C]"), ("delta", "nino12", "ΔTSM Niño 1+2 [°C]"),
                 ("delta_relativo", "nino34", "ΔTSM rel. Niño 3.4 [°C]"),
                 ("delta_relativo", "nino12", "ΔTSM rel. Niño 1+2 [°C]"),
                 ("delta_amplitud", "nino34", "Δ amplitud ciclo Niño 3.4 [°C]"),
                 ("delta_amplitud", "nino12", "Δ amplitud ciclo Niño 1+2 [°C]"),
                 ("delta_sigma_3m_pct", "nino34", "ΔAnom$_{3m}$ Niño 3.4 [%]"),
                 ("delta_sigma_3m_pct", "nino12", "ΔAnom$_{3m}$ Niño 1+2 [%]"),
                 ("razon_frec", "ONI", "frec. P/ref ONI"), ("razon_frec", "RONI", "frec. P/ref RONI"),
                 ("razon_frec", "ICEN", "frec. P/ref ICEN")]
    neutro = {"razon_frec": 1}
    fig, axs = plt.subplots(3, 4, figsize=(10, 6), layout="constrained")
    for ax, (var, clave, lab) in zip(axs.flat, variables):
        for g_i, g in enumerate(GRUPOS):
            for e_i, esc in enumerate(escs):
                r = fila_resumen(var, clave, esc, per_sintesis, grupo=g)
                if r is None:
                    continue
                x = g_i + (e_i - (ne - 1) / 2) * 0.22
                ax.errorbar(x, r["mediana"], yerr=[[r["mediana"] - r["p10"]], [r["p90"] - r["mediana"]]],
                            color=COL_ESC[esc], lw=1.2, capsize=2)
                ax.plot(x, r["mediana"], "o", ms=7, mec=COL_ESC[esc], mew=1.4,
                        mfc=COL_ESC[esc] if r["signif"] else "white")
        ax.axhline(neutro.get(var, 0), color="0.4", lw=0.8, ls="--")
        ax.set_xticks(range(len(GRUPOS)), [f"{g}" for g in GRUPOS])
        ax.set_xlabel("modelos en el conjunto", fontsize=8)
        ax.set_title(lab, fontsize=9)
    axs.flat[-1].axis("off")
    axs.flat[-1].legend(handles=[Line2D([], [], marker="o", color=COL_ESC[e], label=NOM_ESC[e]) for e in escs] +
                        [Line2D([], [], ls="", marker="o", mfc="k", mec="k", label="significativo (Holm)"),
                         Line2D([], [], ls="", marker="o", mfc="white", mec="k", label="no significativo")],
                        loc="center", frameon=False)
    fig.suptitle(f"Mediana y percentiles 10-90 del cambio en {NOM_PER[per_sintesis]}, por conjunto de modelos")
    guardar(fig, "A10_sensibilidad_conjuntos")


if __name__ == "__main__":
    main()
