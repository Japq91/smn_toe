#!/usr/bin/env python3
"""plotA01 -- Figura A1 del informe E3: figures/e3/e3_A01_mapas_cambio_relativo.png

Mapas del cambio de la TSM relativo al trópico (cambio del punto menos el cambio
medio 20°S-20°N del mismo modelo), mediana del grupo; tramado: acuerdo < 0.8.

Entrada: ens_mapas_ref<ref>.nc (q11) (data/processed/e3/)
Salida: figures/e3/e3_A01_mapas_cambio_relativo.png

Uso: python3 scripts_e3/plotA01_mapas_cambio_relativo.py   (o bash rune3plot.sh A01)
     E3_GRUPO=40 python3 scripts_e3/plotA01_mapas_cambio_relativo.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig = figura_mapas("delta_relativo", "RdBu_r", np.arange(-1.5, 1.51, 0.25), "[°C]",
                       "Cambio de la TSM relativo al trópico", cada=2)
    guardar(fig, "A01_mapas_cambio_relativo")


if __name__ == "__main__":
    main()
