#!/usr/bin/env python3
"""plot04 -- figura e2_02a_ciclo_anual.png (seccion 2a de scripts_e2/plots_e2.ipynb).

Ciclo anual: 40 modelos + ERSSTv5 (absoluto y sin la media anual).

Entrada: climatologia_<caja>_<ref>.csv (p02) + ERSSTv5
Salida: figures/e2/e2_02a_ciclo_anual.png

Uso: python3 scripts_e2/plot04_ciclo_anual.py   (o bash rune2plot.sh 04 04)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    clim, clim_obs = cargar_clim()
    fig, axs = plt.subplots(2, 2, figsize=(12, 5), sharex=True)
    for j, caja in enumerate(CAJAS):
        cl, ob = clim[caja], clim_obs[caja]
        for fila, (datos, obs, ylab) in enumerate([(cl, ob, "TSM [°C]"),
                                                   (cl.sub(cl.mean(axis=1), axis=0), ob - ob.mean(), "TSM - media anual [°C]")]):
            ax = axs[fila, j]
            ax.plot(range(1, 13), datos.T.values, color="0.6", alpha=0.45, lw=0.7)
            ax.plot(range(1, 13), datos.mean(), color="tab:red", lw=1.8, label="media multimodelo")
            ax.plot(range(1, 13), obs.values, color="k", lw=2, label="ERSSTv5")
            ax.set_ylabel(ylab)
            if fila == 0:
                ax.set_title(NOM_CAJA[caja])
    axs[0, 0].legend(frameon=False)
    for ax in axs[1]:
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(MESES)
    plt.tight_layout()
    guardar(fig, "02a_ciclo_anual")


if __name__ == "__main__":
    main()
