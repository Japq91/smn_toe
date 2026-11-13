#!/usr/bin/env python3
"""plotA09 -- Figura A9 del informe E3: figures/e3/e3_A09_espectro.png

Espectro de potencia (Welch, segmentos de 256 meses) de ONI, RONI e ICEN en
tramos de igual largo, 86 años cada uno: histórico 1929-2014 frente a cada
escenario 2015-2100 (SSP2-4.5, SSP3-7.0 y SSP5-8.5). Línea: mediana del grupo;
barras: percentiles 10-90, desplazadas en el eje x para que no se tapen;
sombra gris: banda del ENOS, 2-7 años. El histórico es el de los índices
extendidos con SSP2-4.5 (con los otros escenarios es prácticamente igual).

Entrada: ens_espectro_86a.csv (q11) (data/processed/e3/)
Salida: figures/e3/e3_A09_espectro.png

Uso: python3 scripts_e3/plotA09_espectro.py   (o bash rune3plot.sh A09)
     E3_GRUPO=40 python3 scripts_e3/plotA09_espectro.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)

# Colores propios de esta figura (Okabe-Ito, aptos para daltonismo): cuatro
# curvas en el mismo panel necesitan tonos más separados que COL_ESC.
TRAMOS = [("historical", "Histórico 1929-2014", "#1A1A1A"),
          ("ssp245", "SSP2-4.5 2015-2100", "#0072B2"),
          ("ssp370", "SSP3-7.0 2015-2100", "#E69F00"),
          ("ssp585", "SSP5-8.5 2015-2100", "#D55E00")]
FUENTE_HIST = "ssp245"
X_MIN, X_MAX = 1.4, 12       # años por ciclo
DESPLAZA = 0.008             # separación de las barras, en log10 del periodo


def main():
    esp = leer("ens_espectro_86a.csv")
    fig, axs = plt.subplots(3, 1, figsize=(10, 9.5), layout="constrained", sharex=True)
    for i, ind in enumerate(INDICES):
        ax = axs[i]
        ax.axvspan(2, 7, color="0.93", zorder=0)
        for k, (tramo, nombre, col) in enumerate(TRAMOS):
            fuente = FUENTE_HIST if tramo == "historical" else tramo
            d = ens(esp, grupo=GRUPO, fuente=fuente, tramo=tramo, indice=ind).copy()
            d["anios"] = 1 / d["frecuencia"]
            d = d[(d.anios >= X_MIN) & (d.anios <= X_MAX)].sort_values("anios")
            x = d.anios * 10 ** (DESPLAZA * (k - 1.5))
            ax.plot(x, d.mediana, "-o", ms=3.5, lw=1.6, color=col, label=nombre, zorder=3)
            ax.vlines(x, d.p10, d.p90, color=col, lw=1.1, alpha=0.75, zorder=2)
        ax.set_xscale("log")
        ax.set_xlim(X_MIN, X_MAX)
        ax.set_xticks([1.5, 2, 3, 4, 5, 7, 10], ["1.5", "2", "3", "4", "5", "7", "10"])
        ax.xaxis.set_minor_formatter(plt.NullFormatter())
        ax.set_ylim(bottom=0)
        ax.set_ylabel("potencia [°C² año]")
        p0.titulo_panel(ax, LETRAS[i], ind)
    axs[-1].set_xlabel("periodo [años por ciclo]")
    axs[0].legend(frameon=False, fontsize=8.5, loc="upper right", title="86 años cada tramo",
                  title_fontsize=8.5)
    fig.suptitle(f"Espectro de Welch (segmentos de 21 años): histórico 1929-2014 frente a cada escenario 2015-2100\n"
                 f"línea: mediana; barras: percentiles 10-90 de {GRUPO} modelos; sombra: banda del ENOS (2-7 años)")
    guardar(fig, "A09_espectro")


if __name__ == "__main__":
    main()
