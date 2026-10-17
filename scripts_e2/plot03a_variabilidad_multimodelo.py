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
    lim_d = LIM_D          # 5 clases a cada lado de 0: la mitad (-75) y el doble (+150) pesan igual
    lim_iqr = np.arange(0, 151, 15)
    med = dvar.median("number")
    acuerdo_v = np.maximum((dvar > 0).mean("number"), (dvar < 0).mean("number")) >= 0.8
    fig, axs = plt.subplots(2, 1,figsize=(12, 5), sharex=True, layout="constrained")
    im = mapa(axs[0], med, *discreta("PuOr_r", lim_d), "Δσ mediana multimodelo -- punteado: ≥80% de modelos con el mismo signo", punteado=acuerdo_v, letra="a")
    barra(fig, im, axs[0], "[%]", lim_d, extend="both", pad=.01)
    iqr = dvar.quantile(0.75, "number") - dvar.quantile(0.25, "number")
    im = mapa(axs[1], iqr, *discreta("magma_r", lim_iqr), "Rango intercuartil entre modelos", letra="b")
    barra(fig, im, axs[1], "[%]", lim_iqr, extend="max", pad=.01)
    # plt.tight_layout()
    guardar(fig, "03a_variabilidad_multimodelo")


if __name__ == "__main__":
    main()
