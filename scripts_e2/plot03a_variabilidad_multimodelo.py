#!/usr/bin/env python3
"""plot03a -- figura e2_03a_variabilidad_multimodelo.png (seccion 3a de scripts_e2/plots_e2.ipynb).

Variabilidad: mediana multimodelo, acuerdo de signo y dispersion entre modelos.

Entrada: variabilidad_tsm_ref<ref>.nc (p04)
Salida: figures/e2/e2_03a_variabilidad_multimodelo.png

Uso: python3 scripts_e2/plot03a_variabilidad_multimodelo.py   (o bash rune2plot.sh 03a 03a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    dvar = cargar_dvar()
    norm_v = mcolors.TwoSlopeNorm(0, -75, 150)
    med = dvar.median("number")
    acuerdo_v = np.maximum((dvar > 0).mean("number"), (dvar < 0).mean("number")) >= 0.8
    fig, axs = plt.subplots(2, 1,figsize=(12, 5),sharex=True, constrained_layout=True)
    im = mapa(axs[0], med, "PuOr_r", norm_v, "Δσ mediana multimodelo -- punteado: ≥80% de modelos con el mismo signo", punteado=acuerdo_v)
    fig.colorbar(im, ax=axs[0], label="[%]", extend="both", shrink=0.9)
    iqr = dvar.quantile(0.75, "number") - dvar.quantile(0.25, "number")
    im = mapa(axs[1], iqr, "magma_r", mcolors.Normalize(0, 150), "Rango intercuartil entre modelos")
    fig.colorbar(im, ax=axs[1], label="[%]", extend="max", shrink=.9,pad=.01)
    # plt.tight_layout()
    guardar(fig, "03a_variabilidad_multimodelo")


if __name__ == "__main__":
    main()
