#!/usr/bin/env python3
"""plotA08 -- Figura A8 del informe E3: figures/e3/e3_A08_tipo_eventos.png

(a) Eventos por 30 años según su tipo, media del grupo: costero (ICEN sin ONI),
extendido (ICEN y ONI superpuestos) y central (ONI sin ICEN). (b) Fracción de
eventos del ICEN que son costeros, por modelo.

Entrada: cambio_eventos_ref<ref>.csv (q08), resumen_multimodelo_ref<ref>.csv (q10) (data/processed/e3/)
Salida: figures/e3/e3_A08_tipo_eventos.png

Uso: python3 scripts_e3/plotA08_tipo_eventos.py   (o bash rune3plot.sh A08)
     E3_GRUPO=40 python3 scripts_e3/plotA08_tipo_eventos.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    col_tipo = {"costero": "#009E73", "extendido": "#CC79A7", "central": "#0072B2"}
    ev = cambio_ev()
    cats = cats_todo()
    fig, axs = plt.subplots(2, 1, figsize=(7, 5), layout="constrained")
    ax = axs[0]
    icen = ens(ev, indice="ICEN").set_index(["escenario", "periodo", "number"]).sort_index()
    oni = ens(ev, indice="ONI").set_index(["escenario", "periodo", "number"]).sort_index()
    base = np.zeros(len(cats))
    for tipo, tabla, col in [("costero", icen, "n_costero"), ("extendido", icen, "n_extendido"),
                             ("central", oni, "n_central")]:
        v = np.array([(tabla.loc[(e, p)].loc[SEL, col] / tabla.loc[(e, p)].loc[SEL, "siglos"]).mean() * ANIOS_PERIODO / 100
                      for e, p in cats])
        ax.bar(range(len(cats)), v, bottom=base, color=col_tipo[tipo], edgecolor="white", lw=1.5, width=0.7,
               label=tipo)
        base += v
    ax.set_xticks(range(len(cats)), [etiqueta_cat(e, p) for e, p in cats], fontsize=8)
    ax.set_ylabel("eventos / 30 años\n(media del grupo)")
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
    p0.titulo_panel(ax, "a", f"Eventos por tipo {GRUPO} modelos")
    tira(axs[1], ev, "frac_costero", cats, "indice", "ICEN", ylabel="fracción de eventos ICEN")
    p0.titulo_panel(axs[1], "b", "Fracción costera", pad=14)
    leyenda_tira(fig, cambio=False)
    guardar(fig, "A08_tipo_eventos")


if __name__ == "__main__":
    main()
