#!/usr/bin/env python3
"""plot04c -- figura e2_04c_asimetria_oni_icen.png (seccion 4c de scripts_e2/plots_e2.ipynb).

Forma de la distribucion de ONI e ICEN, una columna por indice:
  fila 1 -- curtosis (exceso) vs asimetria, un circulo por modelo (color =
            numero de modelo, barra turbo continua); rombo = ERSSTv5, lineas
            punteadas = valores de ERSSTv5 y cruz roja = la normal (0, 0).
  fila 2 -- densidad (KDE) de la serie mensual: ERSSTv5 en negro, la normal
            con la media y sigma de ERSSTv5 en rojo, cada modelo en gris fino.

Entrada: indices_enso_<y0>-<y1>.csv (p01) + OBS
Salida: figures/e2/e2_04c_asimetria_oni_icen.png

Uso: python3 scripts_e2/plot04c_asimetria_oni_icen.py   (o bash rune2plot.sh 04c 04c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    est, df = cargar_est(), cargar_indices()
    cmap, norm, ticks = cmap_modelos(continua=True, nombre="turbo")
    col = cmap(norm([int(n[1:]) for n in numbers]))   # color del modelo (barra 1..40)
    fig, axs = plt.subplots(2, 2, figsize=(13, 9), height_ratios=[1.2, 1], layout="constrained")
    for j, (ind, nom) in enumerate([("ONI", "ONI (Niño3.4)"), ("ICEN", "ICEN (Niño1+2)")]):
        # fila 1: curtosis vs asimetria
        ax = axs[0, j]
        x, y = f"skew_{ind}", f"kurt_{ind}"
        ax.scatter(est.loc[numbers, x], est.loc[numbers, y], marker="o", s=50, facecolor="none",
                   edgecolor=col, lw=1.3)
        ax.scatter(est.loc["OBS", x], est.loc["OBS", y], marker="D", s=50, c="k", label="ERSSTv5", zorder=3)
        ax.scatter(0, 0, marker="P", s=60, c="tab:red", label="normal", zorder=3)
        ax.axhline(est.loc["OBS", y], color="k", lw=0.6, ls="--")
        ax.axvline(est.loc["OBS", x], color="k", lw=0.6, ls="--")
        ax.set_xlabel("asimetría")
        ax.set_ylabel("curtosis (exceso)")
        ax.legend(frameon=True)
        titulo_panel(ax, LETRAS[j], f"Asimetría vs curtosis: {nom}")
        # fila 2: distribuciones
        ax = axs[1, j]
        series = {n: df[f"{n}_{ind}"].dropna().values for n in numbers + ["OBS"]}
        lim = max(np.abs(np.concatenate(list(series.values()))).max(), 1)
        xs = np.linspace(-lim, lim, 400)
        for n in numbers:
            ax.plot(xs, stats.gaussian_kde(series[n])(xs), color="0.55", lw=0.4, alpha=0.8)
        ax.plot([], [], color="0.55", lw=0.8, label="40 modelos")   # solo leyenda
        obs = series["OBS"]
        ax.plot(xs, stats.gaussian_kde(obs)(xs), color="k", lw=1.8, label="ERSSTv5")
        ax.plot(xs, stats.norm.pdf(xs, obs.mean(), obs.std(ddof=1)), color="tab:red", lw=1.5,
                label="normal (media y σ de ERSSTv5)")
        ax.set_xlim(-lim, lim)
        ax.set_ylim(bottom=0)
        ax.set_xlabel(f"{ind} [°C]")
        ax.set_ylabel("densidad [1/°C]")
        ax.legend(frameon=True, fontsize=8)
        titulo_panel(ax, LETRAS[j + 2], f"Distribución mensual: {nom}")
    barra_modelos(fig, axs[0, :], cmap, norm, ticks, pad=0.01)
    guardar(fig, "04c_asimetria_oni_icen")

if __name__ == "__main__":
    main()
