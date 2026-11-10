#!/usr/bin/env python3
"""plot09 -- Figura 9 del informe E3: figures/e3/e3_09_duracion_magnitud.png

Duración media, magnitud media del pico, eventos fuertes o más y eventos >= 2σref
(por 30 años), modelo por modelo, para ONI, RONI e ICEN en ref, P1 y P2.
*: P distinto de ref (Wilcoxon pareado + Holm, q10).

Entrada: cambio_eventos_ref<ref>.csv (q08), resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_09_duracion_magnitud.png

Uso: python3 scripts_e3/plot09_duracion_magnitud.py   (o bash rune3plot.sh 09)
     E3_GRUPO=40 python3 scripts_e3/plot09_duracion_magnitud.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    metricas = [("dur_media", "dur. media [meses]"), ("mag_media", "mag. media-pico [°C]"),
                ("n_fuerte_mas", "Ev fuertes o más (30 años)"), ("n_extremo_rel", "Ev ≥ 2σ$_{ref}$ (30 años)")]
    fig, axs = plt.subplots(len(metricas), 3, figsize=(10, 2 * len(metricas)), layout="constrained", sharey="row")
    for i, (m, lab) in enumerate(metricas):
        for j, ind in enumerate(INDICES):
            tira(axs[i, j], cambio_ev(), m, cats_todo(), "indice", ind, ylabel=lab if j == 0 else None)
            p0.titulo_panel(axs[i, j], LETRAS[3 * i + j], ind, pad=14)
    leyenda_tira(fig, cambio=False)
    guardar(fig, "09_duracion_magnitud")


if __name__ == "__main__":
    main()
