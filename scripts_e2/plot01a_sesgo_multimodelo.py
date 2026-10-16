#!/usr/bin/env python3
"""plot01a -- figura e2_01a_sesgo_multimodelo.png (seccion 1a de scripts_e2/plots_e2.ipynb).

Sesgo medio multimodelo, acuerdo de signo y dispersion entre modelos.

Entrada: sesgo_tsm_ref<ref>.nc (p03)
Salida: figures/e2/e2_01a_sesgo_multimodelo.png

Uso: python3 scripts_e2/plot01a_sesgo_multimodelo.py   (o bash rune2plot.sh 01a 01a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    bias = cargar_bias()
    media = bias.mean("number")
    acuerdo = np.maximum((bias > 0).mean("number"), (bias < 0).mean("number")) >= 0.8
    fig, axs = plt.subplots(2, 1, figsize=(12, 5),sharex=True, constrained_layout=True)
    im = mapa(axs[0], media, "RdBu_r", mcolors.TwoSlopeNorm(0, -3, 3),
              "Sesgo medio multimodelo -- punteado: ≥80% de modelos con el mismo signo", punteado=acuerdo, levels=21, extend="both")
    fig.colorbar(im, ax=axs[0], label="[°C]", extend="both", shrink=.9,pad=.01)
    im = mapa(axs[1], bias.std("number"), "managua", mcolors.Normalize(0, 2.5), "Desviación estándar entre modelos", levels=31,)
    fig.colorbar(im, ax=axs[1], label="[°C]", extend="max", shrink=.9,pad=.01)
    # plt.tight_layout()
    guardar(fig, "01a_sesgo_multimodelo")


if __name__ == "__main__":
    main()
