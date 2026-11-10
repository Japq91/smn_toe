#!/usr/bin/env python3
"""plot00_comun_e3 -- configuracion, cargas y funciones de dibujo comunes a
los scripts de figuras del Entregable 3 (scripts_e3/plot<codigo>_<nombre>.py).

No es una figura: lo importan los plot<codigo>_*.py. Salio de las celdas
de configuracion y de funciones de scripts_e3/plots_e3.ipynb (prototipo
local, no versionado); los scripts son la version vigente.

Nomenclatura de las figuras: el codigo es el numero de la figura en el
informe (e3_informe/informe_e3.tex):
  - cuerpo:  01..09   -> figures/e3/e3_01_trayectoria_tsm.png (Figura 1)
  - anexo:   A01..A10 -> figures/e3/e3_A01_mapas_cambio_relativo.png (Figura A1)
y el script que la genera se llama igual: plot01_trayectoria_tsm.py,
plotA01_mapas_cambio_relativo.py. Si se agrega, quita o reordena una
figura del informe, se renombran script y figura para que el codigo siga
siendo el numero de la figura.

Conjunto de modelos que se dibuja en color: variable de entorno E3_GRUPO
("15" por defecto, o "40", "11", "7"). Con un grupo distinto de 15 la
figura se guarda con el sufijo _g<grupo> y no reemplaza a la del informe.

Solo lee data/processed/e3/ (salidas de q01-q11, ./rune3.sh).
"""
import os
import sys
import warnings
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts_e3"))
import common_e3 as c3                      # noqa: E402  periodos, grupos, rutas (y common_e2 como c3.c2)
sys.path.insert(0, str(ROOT / "scripts_e2"))
import plot00_comun as p0                   # noqa: E402  helpers de mapas de E2 (fuerza el backend Agg)

warnings.filterwarnings("ignore", category=RuntimeWarning)

GRUPO = os.environ.get("E3_GRUPO", "15")   # conjunto que se dibuja en color: "15", "40", "11" o "7"

E3 = c3.E3_DIR
OUT_FIG = ROOT / "figures/e3"
OUT_FIG.mkdir(parents=True, exist_ok=True)
REF = c3.etiqueta_periodo("ref")
GRUPOS = c3.grupos()
if GRUPO not in GRUPOS:
    sys.exit(f"E3_GRUPO={GRUPO!r} no es un conjunto de common_e3.grupos(): {list(GRUPOS)}")
SEL = GRUPOS[GRUPO]
ORDEN_SEL = c3.seleccion_e2().query("seleccionado").sort_values("puesto").index.tolist()

# Escenarios: ESCS = los tres (figuras del cuerpo); ESCS_TDR = los dos del
# TdR, para las figuras del anexo en que tres columnas no caben o no aportan.
ESCS = ["ssp245", "ssp370", "ssp585"]   # orden = de menor a mayor forzamiento
ESCS_TDR = ["ssp245", "ssp585"]
NE = len(ESCS)
PERS = list(c3.PERIODOS)               # ref, P1, P2
FUTS = c3.PERIODOS_FUTUROS             # P1, P2
NOM_ESC = {"historical": "Histórico", "ssp245": "2-4.5", "ssp370": "3-7.0", "ssp585": "5-8.5"}
NOM_PER = {p: f"{p} {c3.etiqueta_periodo(p)}" for p in PERS}
NOM_CAJA = {"nino34": "Niño 3.4", "nino12": "Niño 1+2", "tropical": "Trópico 20°S-20°N"}
CAJAS = ["nino34", "nino12"]
INDICES = ["ONI", "RONI", "ICEN"]
MESES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
LETRAS = p0.LETRAS
LON = (120, 290)
ANIOS_PERIODO = 30   # largo de ref, P1 y P2: las frecuencias se muestran en eventos por 30 años

# Colores (Okabe-Ito, seguros para daltonismo): escenario = identidad del
# forzamiento; periodo = tiempo; grupo = conjunto de modelos.
COL_ESC = {"historical": "#4D4D4D", "ssp245": "#E69F00", "ssp370": "#D55E00", "ssp585": "#B2182B"}
COL_PER = {"ref": "#4D4D4D", "P1": "#56B4E9", "P2": "#0B3C8C"}   # tiempo: azules, distintos de los escenarios
COL_GRUPO = {"15": "#000000", "40": "#8C8C8C", "11": "#009E73", "7": "#CC79A7"}
plt.rcParams.update({"hatch.linewidth": 0.4, "hatch.color": "0.45", "axes.spines.top": False,
                     "axes.spines.right": False})


def guardar(fig, nom):
    """Guarda en figures/e3/e3_<nom>.png (con _g<grupo> si GRUPO != 15) y cierra la figura."""
    sufijo = "" if GRUPO == "15" else f"_g{GRUPO}"
    out = OUT_FIG / f"e3_{nom}{sufijo}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Listo: {out.relative_to(ROOT)}", file=sys.stderr)


# ---------------------------------------------------------------------
# Cargas (perezosas y con cache: cada script lee solo lo que usa)
# ---------------------------------------------------------------------

@cache
def leer(nombre, fechas=()):
    path = E3 / nombre
    if not path.exists():
        sys.exit(f"Falta {path}. Correr antes ./rune3.sh (q01-q11).")
    df = pd.read_csv(path, parse_dates=list(fechas) or False)
    if "grupo" in df:
        df["grupo"] = df["grupo"].astype(str)   # para que coincida con las claves de GRUPOS
    return df


def ens_serie():  return leer(f"ens_serie_anual_ref{REF}.csv")
def ens_movil():  return leer("ens_variabilidad_movil_30a.csv")
def ens_estac():  return leer(f"ens_variabilidad_estacional_ref{REF}.csv")
def ens_esp():    return leer(f"ens_espectro_ref{REF}.csv")
def ens_ind():    return leer(f"ens_indices_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.csv", ("time",))
def estado():     return leer(f"estado_medio_ref{REF}.csv")
def amplitud():   return leer(f"ciclo_anual_amplitud_ref{REF}.csv")
def ciclo():      return leer(f"ciclo_anual_ref{REF}.csv")
def variab():     return leer(f"variabilidad_cajas_ref{REF}.csv")
def cambio_ev():  return leer(f"cambio_eventos_ref{REF}.csv")
def resumen():    return leer(f"resumen_multimodelo_ref{REF}.csv")


@cache
def mapas():
    return xr.open_dataset(E3 / f"ens_mapas_ref{REF}.nc")


@cache
def indices(esc):
    return pd.read_csv(c3.find_indices_csv(esc), index_col="time", parse_dates=True)


# ---------------------------------------------------------------------
# Funciones de dibujo
# ---------------------------------------------------------------------

def ens(df, **filtro):
    """Filas de df con columna == valor para cada filtro."""
    m = np.ones(len(df), bool)
    for k, v in filtro.items():
        m &= (df[k] == v).to_numpy()
    return df[m]


def banda(ax, d, x, color, label=None, alpha=0.22, lw=1.6, ls="-"):
    """Mediana (linea) y percentiles 10-90 (sombra) de un producto ens_*."""
    d = d.sort_values(x)
    ax.fill_between(d[x], d["p10"], d["p90"], color=color, alpha=alpha, lw=0)
    ax.plot(d[x], d["mediana"], color=color, lw=lw, ls=ls, label=label)


def periodos_fondo(ax, color="0.92", fechas=False):
    """Sombra gris en ref, P1 y P2."""
    for (y0, y1) in c3.PERIODOS.values():
        if fechas:
            ax.axvspan(pd.Timestamp(f"{y0}-01-01"), pd.Timestamp(f"{y1}-12-31"), color=color, zorder=0)
        else:
            ax.axvspan(y0, y1 + 1, color=color, zorder=0)


def fila_resumen(variable, clave, esc, per, grupo=None):
    """Fila de resumen_multimodelo (q10) o None."""
    r = ens(resumen(), grupo=grupo or GRUPO, variable=variable, caja_indice=clave, escenario=esc, periodo=per)
    return None if r.empty else r.iloc[0]


def etiqueta_cat(esc, per):
    return f"{per}\n{NOM_ESC[esc]}"


def cats_fut(escs=ESCS):
    return [(e, p) for e in escs for p in FUTS]


def cats_todo(escs=ESCS):
    return [(e, p) for e in escs for p in PERS]


def tira(ax, df, valor, cats, clave_col=None, clave=None, variable_res=None, neutro=None, log=False,
         anotar=True, ylabel=None):
    """Un punto por modelo en cada (escenario, periodo) de cats: gris hueco = los
    40; color = los del grupo; barra negra = mediana del grupo. Arriba de cada
    columna futura: acuerdo de signo y * si es significativo (q10)."""
    rng = np.random.default_rng(0)
    for i, (esc, per) in enumerate(cats):
        d = ens(df, escenario=esc, periodo=per)
        if clave_col:
            d = d[d[clave_col] == clave]
        d = d.dropna(subset=[valor])
        x_all = i + rng.uniform(-0.25, 0.25, len(d))
        ax.scatter(x_all, d[valor], s=12, facecolor="none", edgecolor="0.65", lw=0.6, zorder=2)
        s = d[d["number"].isin(SEL)]
        col = COL_PER["ref"] if per == "ref" else COL_ESC[esc]
        ax.scatter(i + rng.uniform(-0.12, 0.12, len(s)), s[valor], s=20, color=col, edgecolor="k",
                   lw=0.3, zorder=3)
        if len(s):
            ax.hlines(s[valor].median(), i - 0.32, i + 0.32, color="k", lw=2.2, zorder=4)
        if anotar and per != "ref":
            r = fila_resumen(variable_res or valor, clave, esc, per)
            if r is not None:
                txt = "*" if bool(r["signif"]) else ""
                if pd.notna(r.get("acuerdo_signo")):
                    txt = f"{r['acuerdo_signo']:.2f}" + txt
                ax.text(i, 1.0, txt, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8)
    if neutro is not None:
        ax.axhline(neutro, color="0.4", lw=0.8, ls="--", zorder=1)
    if log:
        ax.set_yscale("log")
    ax.set_xticks(range(len(cats)), [etiqueta_cat(e, p) for e, p in cats], fontsize=8)
    ax.set_xlim(-0.6, len(cats) - 0.4)
    if ylabel:
        ax.set_ylabel(ylabel)


def leyenda_tira(fig, cambio=True, escs=ESCS, **kw):
    h = ([Line2D([], [], ls="", marker="o", mfc="none", mec="0.65", label="40 modelos")] +
         [Line2D([], [], ls="", marker="o", color=COL_ESC[e], mec="k", label=f"{GRUPO} modelos, {NOM_ESC[e]}")
          for e in escs] +
         [Line2D([], [], color="k", lw=2.2, label=f"mediana de los {GRUPO}")])
    nota = "número: acuerdo de signo · * significativo (Wilcoxon + Holm, p < 0.05)" if cambio else \
           "* P distinto de ref (Wilcoxon pareado + Holm, p < 0.05)"
    h.append(Line2D([], [], ls="", label=nota))
    fig.legend(handles=h, loc="lower center", ncol=len(h) / 2, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.1), **kw)


def mapa_cambio(ax, var, esc, per, cmap, limites, letra=None, titulo=None):
    """Mapa de la mediana del cambio, tramado donde el acuerdo de signo < 0.8."""
    sub = mapas().sel(grupo=GRUPO, escenario=esc, periodo=per, lon=slice(*LON))
    cm, norm = p0.discreta(cmap, limites)
    im = p0.mapa(ax, sub[f"{var}_mediana"], cm, norm, titulo or f"{NOM_ESC[esc]}, {NOM_PER[per]}", letra=letra)
    no_robusto = (sub[f"{var}_acuerdo"] < 0.8).where(sub[f"{var}_mediana"].notnull(), False).astype(float)
    ax.contourf(sub.lon, sub.lat, no_robusto, levels=[0.5, 1.5], colors="none", hatches=["///"], zorder=1.5)
    ax.tick_params(labelsize=8)
    return im


def figura_mapas(var, cmap, limites, unidad, titulo, cada=1, extend="both", escs=ESCS):
    """Filas = escenarios, columnas = P1 y P2."""
    ne = len(escs)
    fig, axs = plt.subplots(ne, 2, figsize=(10, 2 * ne), layout="constrained", sharex=True, sharey=True)
    for i, per in enumerate(FUTS):
        for j, esc in enumerate(escs):
            im = mapa_cambio(axs[j, i], var, esc, per, cmap, limites, letra=LETRAS[ne * j + i])
    p0.barra(fig, im, axs, unidad, limites, cada=cada, extend=extend, shrink=0.6, pad=.005)
    fig.suptitle(f"{titulo} -- mediana de {GRUPO} modelos; tramado: acuerdo de signo < 0.8")
    return fig


# --- cajas (boxplots) entre modelos ------------------------------------

def dibujar_cajas(ax, datos, pos, esc, ancho, etiquetas=None, fmt="{:+.1f}"):
    """Cajas de un escenario en las posiciones pos (distribucion entre modelos):
    caja 25-75, mediana, bigotes 10-90, puntos fuera de ese rango. Gris = historico.
    etiquetas: un valor por caja, escrito en la base del panel bajo su caja."""
    c = COL_ESC[esc]
    ax.boxplot(datos, positions=pos, widths=ancho * 0.85, whis=(10, 90), patch_artist=True, manage_ticks=False,
               boxprops=dict(facecolor="0.8" if esc == "historical" else c, edgecolor=c, lw=0.8),
               medianprops=dict(color="k", lw=1.2),
               whiskerprops=dict(color=c, lw=0.8), capprops=dict(color=c, lw=0.8),
               flierprops=dict(marker="o", ms=2, mfc=c, mec="none", alpha=0.7))
    if etiquetas is not None:
        for x, d, v in zip(pos, datos, etiquetas):
            if len(d) and pd.notna(v):
                ax.text(x, 0.015, fmt.format(v), transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                        rotation=90, fontsize=8, color="k")


def margen_etiquetas(ax, frac=0.16):
    """Baja el limite inferior del eje para que la fila de etiquetas no toque los datos."""
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo - frac * (hi - lo), hi)


def separadores(ax, n):
    for m in np.arange(1.5, n, 1):
        ax.axvline(m, color="0.9", lw=0.6, zorder=0)
    ax.set_xlim(0.5, n + 0.5)


def leyenda_cajas(fig, series, extra=None):
    h = [Patch(facecolor="0.8" if e == "historical" else COL_ESC[e], edgecolor=COL_ESC[e]) for e, _ in series]
    l = [f"{NOM_ESC[e]} {REF}" if e == "historical" else NOM_ESC[e] for e, _ in series]
    if extra:
        h.append(Line2D([], [], ls="")); l.append(extra)
    fig.legend(h, l, loc="outside lower center", ncol=len(h) / 2, frameon=False)


# --- series de indices (Figuras A6 y A7) --------------------------------

def figura_indices(lista, titulo, escs=ESCS_TDR, ejemplo=None):
    """Mediana y p10-p90 del indice mensual (ens_indices) y, en negro, la serie
    de un modelo de ejemplo (por defecto el primero de la seleccion del E2)."""
    ejemplo = ejemplo or ORDEN_SEL[0]
    ne = len(escs)
    fig, axs = plt.subplots(len(lista), ne, figsize=(5 * ne, 2.4 * len(lista) + 0.6), layout="constrained",
                            sharex=True, sharey="row")
    nombre = c3.seleccion_e2().loc[ejemplo, "modelo"]
    for i, ind in enumerate(lista):
        for j, esc in enumerate(escs):
            ax = axs[i, j]
            periodos_fondo(ax, "0.93", fechas=True)
            d = ens(ens_ind(), grupo=GRUPO, escenario=esc, indice=ind)
            banda(ax, d, "time", COL_ESC[esc], f"mediana y p10-p90 ({GRUPO} modelos)", alpha=0.3, lw=0.8)
            s = indices(esc)[f"{ejemplo}_{ind}"]
            ax.plot(s.index, s, color="k", lw=0.35, alpha=0.8, label=f"{ejemplo} ({nombre})")
            for u in (0.5, -0.5):
                ax.axhline(u, color="0.3", lw=0.6, ls=":")
            ax.set_xlim(pd.Timestamp("1950-01-01"), pd.Timestamp("2100-12-31"))
            ax.set_ylabel(f"{ind} [°C]")
            p0.titulo_panel(ax, LETRAS[ne * i + j], f"{ind}, {NOM_ESC[esc]}")
    axs[0, 0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.suptitle(titulo)
    return fig
