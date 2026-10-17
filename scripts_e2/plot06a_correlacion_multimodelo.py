#!/usr/bin/env python3
"""plot06a -- figura e2_06a_correlacion_multimodelo.png (seccion 6a de scripts_e2/plots_e2.ipynb).

Correlacion multimodelo y % de modelos con correlacion significativa.

Entrada: correlacion_tsm_ref<ref>.nc (p06)
Salida: figures/e2/e2_06a_correlacion_multimodelo.png

Uso: python3 scripts_e2/plot06a_correlacion_multimodelo.py   (o bash rune2plot.sh 06a 06a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    corr, pval = cargar_corr()
    fig, axs = plt.subplots(2, 1, figsize=(13, 6.5), layout="constrained")
    frac = (pval < 0.05).mean("number")
    lim_r = np.round(np.arange(-0.6, 0.61, 0.1), 2)
    lim_p = np.arange(0, 101, 10)
    im = mapa(axs[0], corr.mean("number"), *discreta("RdBu_r", lim_r),
              "r medio multimodelo -- punteado: ≥50% de modelos con p<0.05", punteado=frac >= 0.5, letra="a")
    barra(fig, im, axs[0], "r", lim_r, extend="both", pad=.01)
    im = mapa(axs[1], frac * 100, *discreta("viridis", lim_p), "Modelos con correlación significativa (p<0.05) [%]", letra="b")
    barra(fig, im, axs[1], "[%]", lim_p, pad=.01)
    guardar(fig, "06a_correlacion_multimodelo")


if __name__ == "__main__":
    main()
