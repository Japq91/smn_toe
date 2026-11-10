#!/usr/bin/env python3
"""plot02 -- Figura 2 del informe E3: figures/e3/e3_02_mapas_cambio_tsm.png

Mapas del cambio de la TSM media (P - ref), mediana del grupo; filas = escenarios,
columnas = P1 y P2; tramado donde el acuerdo de signo es menor que 0.8.

Entrada: ens_mapas_ref<ref>.nc (q11) (data/processed/e3/)
Salida: figures/e3/e3_02_mapas_cambio_tsm.png

Uso: python3 scripts_e3/plot02_mapas_cambio_tsm.py   (o bash rune3plot.sh 02)
     E3_GRUPO=40 python3 scripts_e3/plot02_mapas_cambio_tsm.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig = figura_mapas("delta_media", "YlOrRd", np.arange(0, 5.01, 0.5), "[°C]", "Cambio de la TSM media",
                       cada=2, extend="max")
    guardar(fig, "02_mapas_cambio_tsm")


if __name__ == "__main__":
    main()
