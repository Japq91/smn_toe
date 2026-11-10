#!/usr/bin/env python3
"""plot04 -- Figura 4 del informe E3: figures/e3/e3_04_mapas_cambio_variabilidad.png

Mapas del cambio porcentual de la desviación estándar de la anomalía mensual sin
tendencia, mediana del grupo; tramado donde el acuerdo de signo es menor que 0.8.

Entrada: ens_mapas_ref<ref>.nc (q11) (data/processed/e3/)
Salida: figures/e3/e3_04_mapas_cambio_variabilidad.png

Uso: python3 scripts_e3/plot04_mapas_cambio_variabilidad.py   (o bash rune3plot.sh 04)
     E3_GRUPO=40 python3 scripts_e3/plot04_mapas_cambio_variabilidad.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    fig = figura_mapas("delta_std_pct", "RdBu_r", np.arange(-50, 50.1, 10), "[%]",
                       "Cambio de la desviación estándar de la anomalía")
    guardar(fig, "04_mapas_cambio_variabilidad")


if __name__ == "__main__":
    main()
