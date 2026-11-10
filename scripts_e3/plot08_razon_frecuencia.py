#!/usr/bin/env python3
"""plot08 -- Figura 8 del informe E3: figures/e3/e3_08_razon_frecuencia.png

Razón entre la frecuencia de eventos cálidos de P1/P2 y la de 1985-2014, modelo por
modelo, para ONI, RONI e ICEN (escala logarítmica). Bajo cada columna: mediana de
eventos por 30 años del grupo (el largo de ref, P1 y P2); junto a la línea 1: la
mediana en ref.

Entrada: cambio_eventos_ref<ref>.csv (q08), resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_08_razon_frecuencia.png

Uso: python3 scripts_e3/plot08_razon_frecuencia.py   (o bash rune3plot.sh 08)
     E3_GRUPO=40 python3 scripts_e3/plot08_razon_frecuencia.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    ev = cambio_ev()

    def mediana_frec(ind, esc, per):
        d = ens(ev, indice=ind, escenario=esc, periodo=per)
        # eventos por 30 años (frec_siglo de q08 x 0.3): el largo de ref, P1 y P2
        return d.loc[d.number.isin(SEL), "frec_siglo"].median() * ANIOS_PERIODO / 100

    cats = cats_fut()
    fig, axs = plt.subplots(3, 1, figsize=(8, 8), layout="constrained", sharey=True)
    for j, ind in enumerate(INDICES):
        ax = axs[j]
        tira(ax, ev, "razon_frec", cats, "indice", ind, neutro=1, log=True, ylabel="frecuencia P / frecuencia ref")
        etiquetas = [f"{etiqueta_cat(esc, per)}\n{mediana_frec(ind, esc, per):.0f} ev/30 años" for esc, per in cats]
        ax.set_xticks(range(len(cats)), etiquetas, fontsize=8)
        # mediana de ref (eventos por siglo) junto a razon = 1. Con bases moviles
        # la ref depende un poco del escenario: si difiere, una por escenario
        refs = {esc: mediana_frec(ind, esc, "ref") for esc in ESCS}
        if len({round(v, 1) for v in refs.values()}) == 1:
            ax.text(0.012, 1.04, f"ref: {next(iter(refs.values())):.0f} ev/30 años", transform=ax.get_yaxis_transform(),
                    rotation=90, ha="left", va="bottom", fontsize=7.5, color=COL_PER["ref"])
        else:
            for k, (e, v) in enumerate(refs.items()):
                ax.text(0.012 + 0.022 * k, 1.04, f"ref: {v:.0f}", transform=ax.get_yaxis_transform(), rotation=90,
                        ha="left", va="bottom", fontsize=7.5, color=COL_ESC[e], fontweight="bold")
        p0.titulo_panel(ax, LETRAS[j], ind, pad=14)
    axs[0].set_yticks([0.25, 0.5, 1, 2, 4])
    axs[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
    axs[0].yaxis.set_minor_formatter(plt.NullFormatter())
    leyenda_tira(fig)
    fig.suptitle(f"Razón de frecuencias P / ref\nbajo cada categoría: mediana de eventos por 30 años de los "
                 f"{GRUPO} modelos en ese periodo", fontsize=10)
    guardar(fig, "08_razon_frecuencia")


if __name__ == "__main__":
    main()
