#!/usr/bin/env python3
"""plot07e -- figura e2_07e_duracion_estacionalidad.png (seccion 7e de scripts_e2/plots_e2.ipynb).

Distribucion de duraciones y estacionalidad del pico (mes calendario).

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07)
Salida: figures/e2/e2_07e_duracion_estacionalidad.png

Uso: python3 scripts_e2/plot07e_duracion_estacionalidad.py   (o bash rune2plot.sh 07e 07e)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    ev = cargar_eventos()
    fig, axs = plt.subplots(2, 3, figsize=(15, 7))
    for j, i in enumerate(INDICES):
        e = ev[i]
        mod, obs = e[e["number"] != "OBS"], e[e["number"] == "OBS"]
        bins = np.arange(0, max(e["duracion_meses"].max(), 24) + 2, 2)
        axs[0, j].hist(mod["duracion_meses"], bins=bins, density=True, color=COL_IDX[i], alpha=0.6, label="40 modelos")
        axs[0, j].hist(obs["duracion_meses"], bins=bins, density=True, histtype="step", color="k", lw=1.6, label="ERSSTv5")
        axs[0, j].set_xlabel("duración (meses)")
        axs[0, j].set_title(i)
        hm = mod["fecha_pico"].dt.month.value_counts(normalize=True).reindex(range(1, 13), fill_value=0)
        ho = obs["fecha_pico"].dt.month.value_counts(normalize=True).reindex(range(1, 13), fill_value=0)
        axs[1, j].bar(range(1, 13), hm, color=COL_IDX[i], alpha=0.6, label="40 modelos")
        axs[1, j].step(np.arange(0.5, 13.5), np.r_[ho.values, ho.values[-1]], where="post", color="k", lw=1.6, label="ERSSTv5")
        axs[1, j].set_xticks(range(1, 13))
        axs[1, j].set_xticklabels(MESES)
        axs[1, j].set_xlabel("mes del pico")
    axs[0, 0].set_ylabel("densidad")
    axs[1, 0].set_ylabel("fracción de eventos")
    axs[0, 0].legend(frameon=False)
    plt.tight_layout()
    guardar(fig, "07e_duracion_estacionalidad")


if __name__ == "__main__":
    main()
