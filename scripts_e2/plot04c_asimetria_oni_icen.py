#!/usr/bin/env python3
"""plot04c -- figura e2_04c_asimetria_oni_icen.png (seccion 4c de scripts_e2/plots_e2.ipynb).

Forma de la distribucion de ONI e ICEN, una columna por indice:
  fila 1 -- curtosis (exceso) vs asimetria, un circulo por modelo (color =
            numero de modelo, barra turbo continua); rombo = ERSSTv5, lineas
            punteadas = valores de ERSSTv5 y cruz roja = la normal (0, 0).
  fila 2 -- densidad (KDE) de la serie mensual: ERSSTv5 en negro, la normal
            con la media y sigma de ERSSTv5 en rojo, cada modelo en gris fino;
            franjas de fondo = categorias frias (azul) y calidas (rojo) de
            cada indice, blanco = neutro (ver CATEGORIAS).

Entrada: indices_enso_<y0>-<y1>.csv (p01) + OBS
Salida: figures/e2/e2_04c_asimetria_oni_icen.png

Uso: python3 scripts_e2/plot04c_asimetria_oni_icen.py   (o bash rune2plot.sh 04c 04c)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


# Limites de las categorias ENOS (frio <- neutro -> calido), en [°C]:
#   ONI  -- NOAA CPC: debil 0.5, moderado 1.0, fuerte 1.5, muy fuerte 2.0 (simetrico)
#   ICEN -- ENFEN 01-2024, Tabla 2: frias -0.7/-1.1/-1.3, calidas 0.5/1.3/2.1/3.5
CATEGORIAS = {
    "ONI": dict(frio=[-0.5, -1.0, -1.5, -2.0], calido=[0.5, 1.0, 1.5, 2.0]),
    "ICEN": dict(frio=[-0.7, -1.1, -1.3], calido=[0.5, 1.3, 2.1, 3.5]),
}


def franjas(ax, ind, lim):
    """Franjas de fondo por categoria: azules (frio) y rojos (calido) cada vez
    mas intensos, blanco en el rango neutro."""
    for lado, cmap in [("frio", plt.get_cmap("Blues")), ("calido", plt.get_cmap("Reds"))]:
        bordes = CATEGORIAS[ind][lado] + [np.sign(CATEGORIAS[ind][lado][0]) * lim]
        for k, (a, b) in enumerate(zip(bordes[:-1], bordes[1:])):
            ax.axvspan(a, b, color=cmap(0.1 + 0.07 * k), alpha=0.6, lw=0, zorder=0)
    for v in CATEGORIAS[ind]["frio"] + CATEGORIAS[ind]["calido"]:
        ax.axvline(v, color="0.6", lw=0.4, zorder=0)


def main():
    est, df = cargar_est(), cargar_indices()
    cmap, norm, ticks = cmap_modelos(continua=True, nombre="turbo")
    col = cmap(norm([int(n[1:]) for n in numbers]))   # color del modelo (barra 1..40)
    fig, axs = plt.subplots(2, 2, figsize=(12, 6), height_ratios=[1.2, .9], layout="constrained",sharey='row',sharex='row')
    for j, (ind, nom) in enumerate([("ONI", "ONI (Niño3.4)"), ("ICEN", "ICEN (Niño1+2)")]):
        # fila 1: curtosis vs asimetria
        ax = axs[0, j]
        x, y = f"skew_{ind}", f"kurt_{ind}"
        ax.scatter(est.loc[numbers, x], est.loc[numbers, y], marker="o", s=50, facecolor="none",
                   edgecolor=col, lw=.9)
        ax.scatter(est.loc["OBS", x], est.loc["OBS", y], marker="D", s=30, c="k", label="ERSSTv5", zorder=3)
        ax.scatter(0, 0, marker="P", s=30, c="tab:red", label="normal", zorder=3)
        ax.axhline(est.loc["OBS", y], color="k", lw=0.5, ls="--")
        ax.axvline(est.loc["OBS", x], color="k", lw=0.5, ls="--")
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
        franjas(ax, ind, lim)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(bottom=0)
        ax.set_xlabel(f"{ind} [°C]")
        ax.set_ylabel("densidad [1/°C]")
        ax.legend(frameon=True, fontsize=8)
        titulo_panel(ax, LETRAS[j + 2], f"Distribución mensual: {nom}")
    barra_modelos(fig, axs[0, -1], cmap, norm, ticks[::2], alto=0.8, ancho=0.025, pad=0.02)  # solo la fila de arriba
    guardar(fig, "04c_asimetria_oni_icen")

if __name__ == "__main__":
    main()
