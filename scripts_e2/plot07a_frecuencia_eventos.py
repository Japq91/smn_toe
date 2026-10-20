#!/usr/bin/env python3
"""plot07a -- figura e2_07a_frecuencia_eventos.png (seccion 7a de scripts_e2/plots_e2.ipynb).

Frecuencia de eventos por categoria (oficial y relativa), eventos por siglo.

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07), indices_enso_<y0>-<y1>.csv (p01)
Salida: figures/e2/e2_07a_frecuencia_eventos.png

Uso: python3 scripts_e2/plot07a_frecuencia_eventos.py   (o bash rune2plot.sh 07a 07a)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    ev, siglos = cargar_eventos(), cargar_siglos()
    fig, axs = plt.subplots(3, 2, figsize=(10, 6), sharex=True, sharey=True)
    for fila, i in enumerate(INDICES):
        for col, (campo, orden, cmap) in enumerate([("categoria_oficial", ORD_OF, "YlOrRd"), ("categoria_relativa", ORD_REL, "PuRd")]):
            t = ev[i].groupby("number")[campo].value_counts().unstack(fill_value=0).reindex(datasets, fill_value=0)
            t = t[[c for c in orden if c in t.columns]]
            t = t.div([siglos[(n, i)] for n in t.index], axis=0)
            ax = axs[fila, col]
            t.plot.bar(stacked=True, ax=ax, width=0.85, colormap=cmap, edgecolor="k", lw=0.2, legend=(fila == 0))
            ax.axhline(t.loc["OBS"].sum(), color="k", ls="--", lw=0.9)
            ax.set_ylabel(f"[eventos/siglo]")
            titulo_panel(ax, LETRAS[2 * fila + col], f"{i}: {campo.replace('_', ' ')}")
            if fila == 0:
                ax.legend(fontsize=7, ncol=len(orden), frameon=False, loc="upper right")
    for ax in axs[-1]:
        ax.set_xticklabels([etiqueta.get(n, "ERSSTv5") for n in datasets], rotation=90, fontsize=6)
        ax.get_xticklabels()[-1].set_fontweight("bold")
    plt.tight_layout()
    guardar(fig, "07a_frecuencia_eventos")


if __name__ == "__main__":
    main()
