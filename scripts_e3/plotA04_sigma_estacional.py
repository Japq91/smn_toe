#!/usr/bin/env python3
"""plotA04 -- Figura A4 del informe E3: figures/e3/e3_A04_sigma_estacional.png

Anom3m por estación (trimestre centrado en cada mes) en ref, P1 y P2, mediana y p10-p90
del grupo, para SSP2-4.5 y SSP5-8.5.

Entrada: ens_variabilidad_estacional_ref<ref>.csv (q11) (data/processed/e3/)
Salida: figures/e3/e3_A04_sigma_estacional.png

Uso: python3 scripts_e3/plotA04_sigma_estacional.py   (o bash rune3plot.sh A04)
     E3_GRUPO=40 python3 scripts_e3/plotA04_sigma_estacional.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    escs = ESCS_TDR
    fig, axs = plt.subplots(2, len(escs), figsize=(10, 6), layout="constrained", sharex=True, sharey="row")
    for i, caja in enumerate(CAJAS):
        for j, esc in enumerate(escs):
            ax = axs[i, j]
            for per in PERS:
                banda(ax, ens(ens_estac(), grupo=GRUPO, escenario=esc, caja=caja, periodo=per, variable="sigma_3m"),
                      "mes", COL_PER[per], NOM_PER[per])
            ax.set_xticks(range(1, 13), MESES)
            ax.set_ylabel("Anom$_{3m}$ [°C]")
            p0.titulo_panel(ax, LETRAS[len(escs) * i + j], f"{NOM_CAJA[caja]}, {NOM_ESC[esc]}")
    axs[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle(f"Anom$_{{3m}}$ por estación -- mediana y percentiles 10-90 de {GRUPO} modelos")
    guardar(fig, "A04_sigma_estacional")


if __name__ == "__main__":
    main()
