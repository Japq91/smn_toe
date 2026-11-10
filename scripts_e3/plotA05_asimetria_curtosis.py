#!/usr/bin/env python3
"""plotA05 -- Figura A5 del informe E3: figures/e3/e3_A05_asimetria_curtosis.png

Asimetría g1 y curtosis en exceso g2 de la anomalía de Niño 3.4 y Niño 1+2 en ref y
P2, por modelo (flecha ref -> P2) y mediana del grupo (rombo), por escenario.

Entrada: variabilidad_cajas_ref<ref>.csv (q05) (data/processed/e3/)
Salida: figures/e3/e3_A05_asimetria_curtosis.png

Uso: python3 scripts_e3/plotA05_asimetria_curtosis.py   (o bash rune3plot.sh A05)
     E3_GRUPO=40 python3 scripts_e3/plotA05_asimetria_curtosis.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig, axs = plt.subplots(NE, 2, figsize=(8, 3.5 * NE), layout="constrained", sharex=True, sharey=True)
    for i, esc in enumerate(ESCS):
        for j, caja in enumerate(CAJAS):
            ax = axs[i, j]
            d = ens(variab(), escenario=esc, caja=caja).set_index(["number", "periodo"])
            for n in SEL:
                r, f = d.loc[(n, "ref")], d.loc[(n, "P2")]
                ax.annotate("", (f.asimetria, f.curtosis), (r.asimetria, r.curtosis),
                            arrowprops=dict(arrowstyle="->", color="0.6", lw=0.6))
            for per, col in [("ref", COL_PER["ref"]), ("P2", COL_ESC[esc])]:
                s = d.xs(per, level="periodo").loc[SEL]
                ax.scatter(s.asimetria, s.curtosis, s=18, color=col, edgecolor="k", lw=0.3, zorder=3,
                           label=f"{per} (cada modelo)")
                ax.scatter(s.asimetria.median(), s.curtosis.median(), s=45, marker="D", color=col, edgecolor="k",
                           zorder=4, label=f"{per} (mediana)")
            ax.axhline(0, color="0.5", lw=0.6)
            ax.axvline(0, color="0.5", lw=0.6)
            ax.set_xlabel("asimetría $g_1$")
            ax.set_ylabel("curtosis en exceso $g_2$")
            p0.titulo_panel(ax, LETRAS[2 * i + j], f"{NOM_CAJA[caja]}, {NOM_ESC[esc]}: ref → P2")
            ax.legend(frameon=False, fontsize=7)
    guardar(fig, "A05_asimetria_curtosis")


if __name__ == "__main__":
    main()
