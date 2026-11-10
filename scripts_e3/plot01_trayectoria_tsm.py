#!/usr/bin/env python3
"""plot01 -- Figura 1 del informe E3: figures/e3/e3_01_trayectoria_tsm.png

Trayectoria de la TSM anual 1850-2100 en Niño 3.4 (columna izquierda) y Niño 1+2
(derecha): arriba la anomalía respecto de 1985-2014 (base fija), abajo la anomalía
menos la del trópico 20°S-20°N. Mediana y p10-p90 del grupo, por escenario.

Entrada: ens_serie_anual_ref<ref>.csv (q11) (data/processed/e3/)
Salida: figures/e3/e3_01_trayectoria_tsm.png

Uso: python3 scripts_e3/plot01_trayectoria_tsm.py   (o bash rune3plot.sh 01)
     E3_GRUPO=40 python3 scripts_e3/plot01_trayectoria_tsm.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    serie = ens_serie()
    fig, axs = plt.subplots(2, 2, figsize=(10, 6), layout="constrained", sharex=True, sharey="row")
    for j, caja in enumerate(CAJAS):
        for i, var in enumerate(["anom", "anom_relativa"]):
            ax = axs[i, j]
            periodos_fondo(ax)
            h = ens(serie, grupo=GRUPO, caja=caja, variable=var, escenario="ssp245")
            banda(ax, h[h.year <= 2014], "year", COL_ESC["historical"], "historical")
            for esc in ESCS:
                d = ens(serie, grupo=GRUPO, caja=caja, variable=var, escenario=esc)
                banda(ax, d[d.year >= 2014], "year", COL_ESC[esc], NOM_ESC[esc])
            ax.axhline(0, color="0.4", lw=0.7)
            ax.set_xlim(1850, 2100)
            ax.set_ylabel("[°C]")
            tit = NOM_CAJA[caja] + (" -- anomalía 1985-2014" if i == 0 else " -- menos trópico")
            p0.titulo_panel(ax, LETRAS[2 * i + j], tit)
    for nom, (y0, y1) in c3.PERIODOS.items():
        axs[0, 0].text((y0 + y1 + 1) / 2, 0.97, nom, transform=axs[0, 0].get_xaxis_transform(), ha="center",
                       va="top", fontsize=10, color="0.3")
    axs[0, 0].legend(loc="upper left", frameon=False, fontsize=8)
    fig.suptitle(f"TSM anual -- p50 y [p10-p90] de {GRUPO} modelos")
    guardar(fig, "01_trayectoria_tsm")


if __name__ == "__main__":
    main()
