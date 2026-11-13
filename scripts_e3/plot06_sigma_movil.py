#!/usr/bin/env python3
"""plot06 -- Figura 6 del informe E3: figures/e3/e3_06_sigma_movil.png

Cambio de Anom3m en ventanas móviles de 30 años respecto de 1985-2014, mediana y
p10-p90 del grupo, por escenario.

Entrada: ens_variabilidad_movil_30a.csv (q11) (data/processed/e3/)
Salida: figures/e3/e3_06_sigma_movil.png

Uso: python3 scripts_e3/plot06_sigma_movil.py   (o bash rune3plot.sh 06)
     E3_GRUPO=40 python3 scripts_e3/plot06_sigma_movil.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    movil = ens_movil()
    fig, axs = plt.subplots(2, 1, figsize=(8, 5), layout="constrained")
    for j, caja in enumerate(CAJAS):
        ax = axs[j]
        # ventanas con centro <= 2000 terminan en 2014 o antes: solo historical
        h = ens(movil, grupo=GRUPO, escenario=ESCS[0], caja=caja, variable="delta_sigma_3m_pct")
        banda(ax, h[h.anio_central <= 2000], "anio_central", COL_ESC["historical"], "historical")
        for esc in ESCS:
            d = ens(movil, grupo=GRUPO, escenario=esc, caja=caja, variable="delta_sigma_3m_pct")
            banda(ax, d[d.anio_central >= 2000], "anio_central", COL_ESC[esc], NOM_ESC[esc])
        for nom, (y0, y1) in c3.PERIODOS.items():
            ax.axvline((y0 + y1 + 1) / 2, color="0.6", lw=0.7, ls=":")
            ax.text((y0 + y1 + 1) / 2, 1.0, nom, transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                    fontsize=8)
        ax.axhline(0, color="0.4", lw=0.7)
        ax.set_xlabel("año central de la ventana de 30 años")
        ax.set_ylabel("ΔAnom$_{3m}$ [%]\nrespecto de 1985-2014")
        p0.titulo_panel(ax, LETRAS[j], NOM_CAJA[caja], pad=14)
    axs[0].legend(frameon=False, fontsize=8, loc="upper left", ncol=2)
    fig.suptitle(f"Anom$_{{3m}}$ en ventanas móviles\nmediana y percentiles 10-90 de {GRUPO} modelos", y=1.06)
    guardar(fig, "06_sigma_movil")


if __name__ == "__main__":
    main()
