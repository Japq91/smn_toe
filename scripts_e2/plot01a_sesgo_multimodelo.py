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
    fig, axs = plt.subplots(2, 1, figsize=(12, 4.4), sharex=True, layout="constrained")
    lim_a = np.arange(-3, 3.01, 0.5)
    lim_b = np.arange(0, 2.51, 0.25)
    im = mapa(axs[0], media, *discreta("RdBu_r", lim_a),
              "Sesgo medio multimodelo -- cruces: ≥80% de modelos con el mismo signo", punteado=acuerdo, letra="a")
    barra(fig, im, axs[0], "[°C]", lim_a, extend="both", pad=.01, alto=0.8, cada=2)
    im = mapa(axs[1], bias.std("number"), *discreta("magma", lim_b), "Desviación estándar entre modelos", letra="b")
    barra(fig, im, axs[1], "[°C]", lim_b, extend="max", pad=.01, alto=0.8, cada=2)
    # plt.tight_layout()
    guardar(fig, "01a_sesgo_multimodelo")


if __name__ == "__main__":
    main()
