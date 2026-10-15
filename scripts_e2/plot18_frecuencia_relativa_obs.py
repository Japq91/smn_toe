#!/usr/bin/env python3
"""plot18 -- figura e2_07b_frecuencia_relativa_obs.png (seccion 7b de scripts_e2/plots_e2.ipynb).

Mapa de calor de frecuencia por categoria oficial, relativa a ERSSTv5.

Entrada: eventos_<INDICE>_<y0>-<y1>.csv (p07), indices_enso_<y0>-<y1>.csv (p01)
Salida: figures/e2/e2_07b_frecuencia_relativa_obs.png

Uso: python3 scripts_e2/plot18_frecuencia_relativa_obs.py   (o bash rune2plot.sh 18 18)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    ev, siglos = cargar_eventos(), cargar_siglos()
    fig, axs = plt.subplots(1, 3, figsize=(14, 9), sharey=True)
    for ax, i in zip(axs, INDICES):
        t = ev[i].groupby("number")["categoria_oficial"].value_counts().unstack(fill_value=0).reindex(datasets, fill_value=0)
        t = t[[c for c in ORD_OF if c in t.columns]]
        t = t.div([siglos[(n, i)] for n in t.index], axis=0)
        t["total"] = t.sum(axis=1)
        r = np.log2((t.loc[numbers] + 0.25) / (t.loc["OBS"] + 0.25))   # +0.25 evita log(0)
        im = ax.imshow(r.values, cmap="BrBG_r", vmin=-2, vmax=2, aspect="auto")
        ax.set_xticks(range(r.shape[1]))
        ax.set_xticklabels(r.columns, rotation=45, ha="right")
        ax.set_title(f"{i}  (OBS: " + ", ".join(f"{v:.0f}" for v in t.loc["OBS"]) + ")", fontsize=8)
    axs[0].set_yticks(range(len(numbers)))
    axs[0].set_yticklabels([etiqueta[n] for n in numbers], fontsize=7)
    fig.colorbar(im, ax=axs, shrink=0.5, label="log2(frecuencia modelo / ERSSTv5)", extend="both")
    guardar(fig, "07b_frecuencia_relativa_obs")


if __name__ == "__main__":
    main()
