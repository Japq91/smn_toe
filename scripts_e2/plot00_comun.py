#!/usr/bin/env python3
"""plot00 -- configuracion, helpers de dibujo y carga de datos compartidos
por los scripts de figuras de E2 (scripts_e2/plot01_*.py ... plot28_*.py).

No genera ninguna figura: cada plotNN_*.py hace 'from plot00_comun import *'
y dibuja una sola figura, con el mismo codigo de la seccion correspondiente
de scripts_e2/plots_e2.ipynb (de donde salieron estos scripts). Las
figuras se guardan en figures/e2/e2_<seccion>_<nombre>.png -- mismo nombre
que el notebook, que es el que citan informe/borradores/.

Datos de entrada: data/processed/e2/ (salidas de p01-p09, ver rune2.sh).
Las cargas comunes van con lru_cache: un script que usa varias (ej.
plot28_portrait_resumen.py) lee cada archivo una sola vez.
"""
import logging
import sys
import warnings
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # sin ventana: se corre desde terminal/rune2plot.sh
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from scipy import signal, stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts_e2"))
import common_e2 as c2
import p08_taylor_compuesto as p08   # solo para reusar composite_curve (no corre nada)
sys.path.insert(0, str(ROOT / "scripts"))
import plot_common as pc

# "Times New Roman" puede no estar instalada: matplotlib cae a la
# siguiente serif, sin llenar el log con un aviso por cada texto.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
# Estadisticos multimodelo (std, mediana) sobre puntos de tierra, todo
# NaN: el resultado es NaN (correcto, se pinta gris), sin los avisos de numpy.
for _msg in ("Degrees of freedom <= 0 for slice", "All-NaN slice encountered", "Mean of empty slice"):
    warnings.filterwarnings("ignore", message=_msg, category=RuntimeWarning)

E2 = c2.E2_DIR
OUT_FIG = ROOT / "figures/e2"
OUT_FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.size": 10})
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]

REF_INICIO, REF_FIN = 1981, 2014
REF = f"{REF_INICIO}-{REF_FIN}"
PER = c2.indices_period()  # periodo de los indices (p01) -> nombres de p07/p08/p09
VENTANA = 12              # ventana principal de p08/p09 (la que define el ranking oficial)
VENTANAS = [12, 15, 18]   # todo lo que usa el compuesto se muestra con las tres (15 y 18 = sensibilidad)
INDICES = ["ONI", "RONI", "ICEN"]
COL_IDX = {"ONI": "seagreen", "RONI": "steelblue", "ICEN": "#3a8686"}
M_IDX = {"ONI": "^", "RONI": "v", "ICEN": "x"}
CAJAS = {"nino34": pc.NINO34, "nino12": pc.NINO12}
NOM_CAJA = {"nino34": "Niño3.4", "nino12": "Niño1+2"}
MESES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
ORD_OF = ["debil", "moderado", "fuerte", "muy_fuerte", "extraordinario"]
ORD_REL = ["moderado", "fuerte", "extremo"]

# OBS: el .nc enmascarado (data/processed/masked/) puede no estar en esta
# maquina -- en ese caso se usa la copia de data/interim/processed/.
if not c2.obs_path().exists():
    _obs = ROOT / "data/interim/processed/ersstv5_region.nc"
    print(f"Sin {c2.obs_path()} -> se usa {_obs}", file=sys.stderr)
    c2.obs_path = lambda: _obs

registro = pd.DataFrame(c2.read_model_registry()).set_index("number")
numbers = registro.index.tolist()
nombre = registro["model"].to_dict()
etiqueta = {n: f"{n}" for n in numbers}
datasets = numbers + ["OBS"]


def guardar(fig, nom):
    """Guarda en figures/e2/e2_<nom>.png y cierra la figura."""
    out = OUT_FIG / f"e2_{nom}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Listo: {out}", file=sys.stderr)


# ---------------------------------------------------------------------
# Helpers de dibujo
# ---------------------------------------------------------------------

def caja_media(da, box):
    """Media ponderada por cos(lat) de un campo (.., lat, lon) dentro de una caja."""
    sub = da.sel(lon=slice(box["lon1"], box["lon2"]), lat=slice(box["lat2"], box["lat1"]))
    return sub.weighted(np.cos(np.deg2rad(sub.lat))).mean(("lat", "lon"))


def dibujar_cajas(ax, lw=0.9):
    for box, col in [(pc.NINO34, "k"), (pc.NINO12, "m")]:
        x0, x1, y0, y1 = box["lon1"], box["lon2"], box["lat1"], box["lat2"]
        ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color=col, lw=lw)


def mapa(ax, da, cmap, norm, titulo=None, punteado=None, cajas=True, levels=None, extend=None):
    im = da.plot(ax=ax, cmap=cmap, norm=norm, add_colorbar=False, add_labels=False, levels=levels, extend=extend)
    if punteado is not None:
        yy, xx = np.meshgrid(punteado.lat, punteado.lon, indexing="ij")
        m = punteado.values.astype(bool)
        ax.scatter(xx[m], yy[m], s=0.6, c="k", alpha=0.6, linewidths=0)
    if cajas:
        dibujar_cajas(ax)
    if titulo:
        ax.set_title(titulo, fontsize=10)
    ax.set_facecolor("0.85")   # tierra / sin dato en gris
    return im


def multiples(da, cmap, norm, titulo, unidad, punteado=None, lon=(120, 290), ncol=8, orden=None):
    """40 mapas chicos (uno por modelo), recortados al Pacifico tropical."""
    orden = orden or numbers
    nrow = int(np.ceil(len(orden) / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(2.1 * ncol, 1.35 * nrow + 0.8), sharex=True, sharey=True)
    for ax, n in zip(axs.flat, orden):
        k = int(n[1:])
        sub = da.sel(number=k, lon=slice(*lon))
        p = None if punteado is None else punteado.sel(number=k, lon=slice(*lon))
        im = mapa(ax, sub, cmap, norm, punteado=p, levels=21, extend="both")
        ax.set_title(etiqueta[n], fontsize=9, pad=2)
        ax.tick_params(labelsize=8)
    for ax in axs.flat[len(orden):]:
        ax.axis("off")
    fig.subplots_adjust(top=0.93)
    fig.suptitle(titulo, y=0.98)
    fig.colorbar(im, ax=axs, shrink=0.5, pad=0.01, label=unidad, extend="both")
    return fig


def taylor(ax, df, titulo, color=None, rmax=None, etiquetar=True, cbar_label=None):
    """Diagrama de Taylor (cuarto de circulo) a partir de una tabla taylor_*.csv:
    radio = sigma_norm, angulo = arccos(r), arcos grises = RMSE' normalizado."""
    mod = df.drop(index="OBS", errors="ignore")
    rmax = rmax or max(1.6, float(np.ceil(mod["sigma_norm"].max() * 10) / 10) + 0.1)
    t = np.linspace(0, np.pi / 2, 200)
    for r in np.arange(0.25, rmax + 0.01, 0.25):           # sigma constante
        ax.plot(r * np.cos(t), r * np.sin(t), color="0.88", lw=0.6, zorder=0)
    ax.plot(np.cos(t), np.sin(t), color="0.4", lw=0.8, ls="--", zorder=0)
    for e in np.arange(0.25, 2.01, 0.25):                   # RMSE' constante
        tt = np.linspace(0, np.pi, 300)
        x, y = 1 + e * np.cos(tt), e * np.sin(tt)
        ok = (np.hypot(x, y) <= rmax) & (y >= 0)
        ax.plot(x[ok], y[ok], color="tab:green", lw=0.5, alpha=0.5, zorder=0)
    for rc in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]:  # correlacion
        a = np.arccos(rc)
        ax.plot([0, rmax * np.cos(a)], [0, rmax * np.sin(a)], color="0.9", lw=0.5, zorder=0)
        ax.text(1.02 * rmax * np.cos(a), 1.02 * rmax * np.sin(a), f"{rc}", fontsize=6, color="0.4",
                rotation=np.degrees(a), ha="center", va="center")
    th = np.arccos(mod["r"].clip(-1, 1))
    x, y = mod["sigma_norm"] * np.cos(th), mod["sigma_norm"] * np.sin(th)
    sc = ax.scatter(x, y, c=color if color is not None else "tab:blue", cmap="viridis",
                    s=28, edgecolor="k", linewidths=0.4, zorder=3)
    if etiquetar:
        for n, xi, yi in zip(mod.index, x, y):
            ax.annotate(n[1:], (xi, yi), fontsize=5.5, xytext=(2, 2), textcoords="offset points")
    ax.scatter([1], [0], marker="*", s=200, c="k", zorder=4, clip_on=False, label="ERSSTv5")
    ax.set_xlim(0, rmax)
    ax.set_ylim(0, rmax)
    ax.set_aspect("equal")
    ax.set_xlabel("σ normalizado")
    ax.set_ylabel("σ normalizado")
    ax.set_title(titulo)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    return sc


# ---------------------------------------------------------------------
# Carga de datos (salidas de p01-p09) y derivados comunes
# ---------------------------------------------------------------------

@lru_cache(maxsize=None)
def cargar_bias():
    """Sesgo de TSM por punto de grid (p03)."""
    return xr.open_dataset(E2 / f"sesgo_tsm_ref{REF}.nc")["bias"]


@lru_cache(maxsize=None)
def cargar_sesgo_caja():
    """Sesgo medio en Niño3.4 / Niño1+2 por modelo (seccion 1c)."""
    bias = cargar_bias()
    sesgo_caja = pd.DataFrame({NOM_CAJA[k]: caja_media(bias, b).to_pandas() for k, b in CAJAS.items()})
    sesgo_caja.index = [f"M{k:02d}" for k in sesgo_caja.index]
    return sesgo_caja


@lru_cache(maxsize=None)
def cargar_clim():
    """(clim, clim_obs): climatologia mensual por caja de los modelos (p02)
    y de ERSSTv5 (recalculada aca, mismo periodo de referencia)."""
    clim, clim_obs = {}, {}
    for caja, box in CAJAS.items():
        clim[caja] = pd.read_csv(E2 / f"climatologia_{caja}_{REF}.csv", index_col="number")
        clim[caja].columns = clim[caja].columns.astype(int)
        serie = c2.box_series(c2.obs_path(), box, "sst", weighted=c2.WEIGHTED[caja])
        clim_obs[caja] = pd.Series(c2.climatology(serie, REF_INICIO, REF_FIN).values, index=range(1, 13))
    return clim, clim_obs


@lru_cache(maxsize=None)
def cargar_tab_clim():
    """Media anual, sesgo, amplitud del ciclo anual y mes mas calido (seccion 2c)."""
    clim, clim_obs = cargar_clim()
    tab = {}
    for caja in CAJAS:
        cl = pd.concat([clim[caja], clim_obs[caja].to_frame("OBS").T])
        tab[(NOM_CAJA[caja], "media (°C)")] = cl.mean(axis=1)
        tab[(NOM_CAJA[caja], "sesgo (°C)")] = cl.mean(axis=1) - clim_obs[caja].mean()
        tab[(NOM_CAJA[caja], "amplitud (°C)")] = cl.max(axis=1) - cl.min(axis=1)
        tab[(NOM_CAJA[caja], "amplitud / OBS")] = (cl.max(axis=1) - cl.min(axis=1)) / (clim_obs[caja].max() - clim_obs[caja].min())
        tab[(NOM_CAJA[caja], "mes máx")] = cl.idxmax(axis=1)
    tab_clim = pd.DataFrame(tab)
    tab_clim.insert(0, ("", "modelo"), [nombre.get(n, "ERSSTv5") for n in tab_clim.index])
    return tab_clim


@lru_cache(maxsize=None)
def cargar_dvar():
    """Diferencia % de sigma de la anomalia por punto de grid (p04)."""
    return xr.open_dataset(E2 / f"variabilidad_tsm_ref{REF}.nc")["std_diff_pct"]


@lru_cache(maxsize=None)
def cargar_var_caja():
    """Δσ medio en Niño3.4 / Niño1+2 por modelo (seccion 3c)."""
    dvar = cargar_dvar()
    var_caja = pd.DataFrame({NOM_CAJA[k]: caja_media(dvar, b).to_pandas() for k, b in CAJAS.items()})
    var_caja.index = [f"M{k:02d}" for k in var_caja.index]
    return var_caja


@lru_cache(maxsize=None)
def cargar_corr():
    """(corr, pval) por punto de grid (p06)."""
    ds_c = xr.open_dataset(E2 / f"correlacion_tsm_ref{REF}.nc")
    return ds_c["corr"], ds_c["sign"]


@lru_cache(maxsize=None)
def cargar_indices():
    """ONI/RONI/ICEN de los 40 modelos (p01) + OBS, indexado por tiempo."""
    return c2.load_all_indices()


@lru_cache(maxsize=None)
def cargar_est():
    """σ, asimetria y curtosis de cada indice por dataset (seccion 4b)."""
    df = cargar_indices()
    filas = []
    for n in numbers + ["OBS"]:
        fila = {"number": n}
        for ind in INDICES:
            s = df[f"{n}_{ind}"].dropna()
            fila[f"σ_{ind}"] = s.std(ddof=1)
            fila[f"skew_{ind}"] = stats.skew(s)
            fila[f"kurt_{ind}"] = stats.kurtosis(s)
        filas.append(fila)
    est = pd.DataFrame(filas).set_index("number")
    est.insert(0, "modelo", [nombre.get(n, "ERSSTv5") for n in est.index])
    return est


@lru_cache(maxsize=None)
def cargar_eventos():
    """Eventos calidos por indice (p07)."""
    return {i: pd.read_csv(E2 / f"eventos_{i}_{PER}.csv", parse_dates=["inicio", "fin", "fecha_pico"]) for i in INDICES}


@lru_cache(maxsize=None)
def cargar_siglos():
    """Largo de cada serie de indice en siglos, para normalizar frecuencias."""
    df = cargar_indices()
    return {(n, i): df[f"{n}_{i}"].notna().sum() / 1200 for n in datasets for i in INDICES}


@lru_cache(maxsize=None)
def cargar_tay():
    """Taylor sobre la serie completa por caja (p05)."""
    return {c: pd.read_csv(E2 / f"taylor_{c}_ref{REF}.csv", index_col="number") for c in CAJAS}


@lru_cache(maxsize=None)
def cargar_skv():
    """Score de p09 por ventana del compuesto."""
    return {v: pd.read_csv(E2 / f"skill_score_vent{v}m_{PER}.csv", index_col="number") for v in VENTANAS}


@lru_cache(maxsize=None)
def cargar_tcv():
    """Taylor del compuesto por ventana e indice (p08)."""
    return {v: {i: pd.read_csv(E2 / f"taylor_compuesto_{i}_vent{v}m_{PER}.csv", index_col="number") for i in INDICES}
            for v in VENTANAS}


def vmin_s():
    """Minimo de S_ONI/S_RONI/S_ICEN entre las tres ventanas (escala de color comun)."""
    skv = cargar_skv()
    return min(skv[v][[f"S_{j}" for j in INDICES]].min().min() for v in VENTANAS)


def orden_s_final():
    """Modelos ordenados por S_final de la ventana principal (lo usan 9b y 10)."""
    return cargar_skv()[VENTANA].sort_values("S_final", ascending=False)


@lru_cache(maxsize=None)
def cargar_curvas():
    """(curvas, n_usados): curvas[v][indice][dataset] = curva compuesta de 2v+1 puntos."""
    df, ev = cargar_indices(), cargar_eventos()
    curvas = {v: {i: {} for i in INDICES} for v in VENTANAS}
    n_usados = {}
    for v in VENTANAS:
        for i in INDICES:
            for n in datasets:
                picos = ev[i].loc[ev[i]["number"] == n, "fecha_pico"].tolist()
                curva, usados, _ = p08.composite_curve(df[f"{n}_{i}"], picos, ventana=v)
                n_usados[(i, f"±{v}m", n)] = usados
                if curva is not None:
                    curvas[v][i][n] = curva
    return curvas, n_usados
