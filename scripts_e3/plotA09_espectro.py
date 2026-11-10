#!/usr/bin/env python3
"""plotA09 -- Figura A9 del informe E3: figures/e3/e3_A09_espectro.png

Espectro de potencia (Welch, segmentos de 15 años) de ONI, RONI e ICEN en ref, P1 y
P2, mediana y p10-p90 del grupo, para SSP2-4.5 y SSP5-8.5; sombra: banda 2-7 años.

Entrada: ens_espectro_ref<ref>.csv (q11) (data/processed/e3/)
Salida: figures/e3/e3_A09_espectro.png

Uso: python3 scripts_e3/plotA09_espectro.py   (o bash rune3plot.sh A09)
     E3_GRUPO=40 python3 scripts_e3/plotA09_espectro.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    escs = ESCS_TDR
    ne = len(escs)
    fig, axs = plt.subplots(3, ne, figsize=(5 * ne, 6), layout="constrained", sharex=True, sharey="row")
    for i, ind in enumerate(INDICES):
        for j, esc in enumerate(escs):
            ax = axs[i, j]
            ax.axvspan(2, 7, color="0.93", zorder=0)
            for per in PERS:
                d = ens(ens_esp(), grupo=GRUPO, escenario=esc, indice=ind, periodo=per).copy()
                d["anios"] = 1 / d["frecuencia"]
                d = d[(d.anios >= 1) & (d.anios <= 15)]
                banda(ax, d, "anios", COL_PER[per], NOM_PER[per])
                ax.plot(d.anios, d.mediana, "o", ms=3, color=COL_PER[per])
            ax.set_xscale("log")
            ax.set_xticks([1, 2, 3, 5, 7, 10, 15], ["1", "2", "3", "5", "7", "10", "15"])
            ax.set_ylabel("potencia [°C² año]")
            if i == 2:
                ax.set_xlabel("periodo [años por ciclo]")
            p0.titulo_panel(ax, LETRAS[ne * i + j], f"{ind}, {NOM_ESC[esc]}")
    axs[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle(f"Espectro de Welch -- mediana y percentiles 10-90 de {GRUPO} modelos; sombra: banda 2-7 años")
    guardar(fig, "A09_espectro")


if __name__ == "__main__":
    main()
