#!/usr/bin/env python3
"""Utilidades compartidas por los scripts q01_*.py, q02_*.py, etc. de
E3 (proyecciones futuras, actividad c) del TdR) -- mismo patron que
scripts_e2/common_e2.py: cada qXX sigue siendo ejecutable por separado.

Reusa de common_e2.py todo lo que ya esta probado en E2 (cajas,
box_series, climatologia, anomalia, bases moviles del CPC, rolling 3m)
en vez de duplicarlo; aca solo vive lo propio de E3:

  - escenarios y periodos (P1/P2 de config/periods.yaml),
  - la serie continua historical + SSP (1850-2100),
  - la seleccion de E2 (los 15 modelos que pasan el filtro de eventos),
  - las variantes de los indices que hacen falta con datos hasta 2100
    (ICEN sin el tope de base 1991-2020, RONI con escala fijada en la
    base, indices con base fija).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import yaml

ROOT = Path(__file__).resolve().parent.parent
E3_DIR = ROOT / "data/processed/e3"

sys.path.insert(0, str(ROOT / "scripts_e2"))
import common_e2 as c2  # noqa: E402  (cajas, box_series, indices de E2)

BOXES = c2.BOXES          # nino34, nino12, tropical
WEIGHTED = c2.WEIGHTED

# Escenarios: SSP2-4.5 y SSP5-8.5 son los del TdR (actividad a/c);
# SSP3-7.0 (descargado, config/periods.yaml lo lista) se suma como
# escenario intermedio opcional. Las figuras del TdR siguen usando solo
# ssp245 y ssp585 (plots_e3.ipynb fija ESCS); ssp370 aparece donde se
# lo pide explicitamente (ej. ESC_02A en la figura 2a).
ESCENARIOS = ["ssp245", "ssp370", "ssp585"]

# Inicio de la serie: 1850, todo el historical. p01 de E2 calcula los
# indices sobre la serie completa desde 1850 y recien despues recorta a
# 1900; las bases moviles del ONI/ICEN de los primeros anios dependen de
# ese inicio, asi que para que el tramo historico coincida con E2 hay
# que partir del mismo anio. Fin: 2100 (CAMS-CSM1-0 e IITM-ESM terminan
# en 2099-12; su 2100 queda NaN).
ANIO_INICIO = 1850
ANIO_FIN = 2100


def _periodos_config():
    with open(ROOT / "config/periods.yaml") as f:
        cfg = yaml.safe_load(f)
    return {k: (cfg[f"proyeccion_{k.lower()}"]["inicio"], cfg[f"proyeccion_{k.lower()}"]["fin"])
            for k in ("P1", "P2")}

# Periodos de comparacion. P1 (2036-2065) y P2 (2071-2100) vienen de
# config/periods.yaml (definidos en E1). La referencia es 1985-2014 y no
# la referencia_historica 1981-2014 de E1/E2, a proposito: con 30 anios,
# igual que P1 y P2, las desviaciones estandar y los conteos de eventos
# se comparan sobre muestras del mismo largo. Es tambien la base fija
# del RONI en E2 (ultimos 30 anios del historical).
PERIODOS = {"ref": (1985, 2014), **_periodos_config()}
PERIODOS_FUTUROS = ["P1", "P2"]
REF = PERIODOS["ref"]


def etiqueta_periodo(nombre):
    y0, y1 = PERIODOS[nombre]
    return f"{y0}-{y1}"


def periodo_de_fecha(fecha):
    """'ref' / 'P1' / 'P2' si el anio cae en uno de los periodos, si no
    None (anios intermedios, ej. 2015-2035)."""
    y = pd.Timestamp(fecha).year
    for nombre, (y0, y1) in PERIODOS.items():
        if y0 <= y <= y1:
            return nombre
    return None


def read_model_registry():
    return c2.read_model_registry()


def seleccion_e2():
    """DataFrame indexado por number (M01..M40) con 'seleccionado' (los
    15 que pasan el filtro de eventos de E2) y 'puesto' (orden por
    S_final dentro de los 15; NaN para los demas). Lo escribe
    scripts_e2/p11_seleccion.py."""
    path = c2.E2_DIR / "seleccion_1900-2014.csv"
    if not path.exists():
        sys.exit(f"Falta {path}. Correr antes ./rune2.sh p11 (seleccion de E2).")
    df = pd.read_csv(path, index_col="number")
    return df[["modelo", "seleccionado", "puesto", "cumple_s09"]]


# Modelos seleccionados con el ICEN mas debil frente a ERSSTv5 (E2,
# Seccion de seleccion: M34 con S_ICEN = 0.45; M40, M35 y M12 con
# S_ICEN < 0.83). El informe de E2 recomienda verificar si la senal
# proyectada cambia al quitarlos.
ICEN_DEBIL = ["M34", "M35", "M12", "M40"]


def grupos():
    """Conjuntos de modelos sobre los que se resumen los resultados:
      15  principal: los que pasan el filtro de eventos de E2
      40  contraste: todos
      11  sensibilidad: los 15 sin ICEN_DEBIL
       7  sensibilidad: el criterio anterior de E2 (pasa el filtro y
          S_final, S_ICEN >= 0.9)
    Devuelve {nombre: [M..]} en ese orden."""
    sel = seleccion_e2()
    s15 = sel.index[sel["seleccionado"]].tolist()
    return {
        "15": s15,
        "40": sel.index.tolist(),
        "11": [n for n in s15 if n not in ICEN_DEBIL],
        "7": sel.index[sel["seleccionado"] & sel["cumple_s09"]].tolist(),
    }


def serie_completa(model, escenario, box_key):
    """Serie mensual cruda (degC) de la caja, historical + escenario
    concatenados, recortada a ANIO_INICIO..ANIO_FIN y reindexada a todos
    los meses del rango (NaN donde el modelo no tiene dato)."""
    partes = [c2.box_series(c2.model_path(model, exp), BOXES[box_key], "tos", weighted=WEIGHTED[box_key])
              for exp in ("historical", escenario)]
    s = xr.concat(partes, dim="time").sortby("time")
    s = s.sel(time=slice(f"{ANIO_INICIO}", f"{ANIO_FIN}"))
    s = s.drop_vars([v for v in s.coords if v != "time"])
    meses = pd.date_range(f"{ANIO_INICIO}-01-01", f"{ANIO_FIN}-12-01", freq="MS")
    return s.reindex(time=meses)


def campo_completo(model, escenario):
    """Campo mensual 2D (time, lat, lon) historical + escenario, para
    los mapas de cambio (q03). Solo se cargan los anios de PERIODOS."""
    partes = []
    for exp in ("historical", escenario):
        ds = xr.open_dataset(c2.model_path(model, exp))
        partes.append(c2._normalize_time(ds["tos"]))
    return xr.concat(partes, dim="time").sortby("time")


def series_cajas():
    """Lee series_cajas_<y0>-<y1>.nc (salida de q01)."""
    path = E3_DIR / f"series_cajas_{ANIO_INICIO}-{ANIO_FIN}.nc"
    if not path.exists():
        sys.exit(f"Falta {path}. Correr antes q01_series_cajas.py.")
    return xr.open_dataset(path)


def recorte(da, nombre_periodo):
    y0, y1 = PERIODOS[nombre_periodo]
    return da.sel(time=slice(f"{y0}", f"{y1}"))


def anomalia_sin_tendencia(da):
    """Anomalia de una ventana de anios: se quita la climatologia
    mensual de la PROPIA ventana y despues la tendencia lineal. Es la
    anomalia con la que se mide la variabilidad en cada periodo (q03,
    q05): sin quitar la tendencia, el calentamiento dentro de los 30
    anios (fuerte en SSP5-8.5) inflaria la desviacion estandar sin que
    cambie el ENOS.

    'time' puede estar en cualquier posicion. Las series sin huecos se
    ajustan todas juntas (np.polyfit vectorizado); las que tienen meses
    faltantes (ej. CAMS-CSM1-0 e IITM-ESM en 2100) se ajustan una por
    una con sus meses validos; las todo-NaN (tierra) quedan NaN."""
    clim = da.groupby("time.month").mean("time")
    anom = (da.groupby("time.month") - clim).drop_vars("month", errors="ignore")
    dims = anom.dims
    anom = anom.transpose("time", ...)
    t = np.arange(anom.sizes["time"], dtype=float)
    vals = anom.values
    plano = vals.reshape(vals.shape[0], -1).copy()
    finito = np.isfinite(plano)
    completas = finito.all(axis=0)
    if completas.any():
        coef = np.polyfit(t, plano[:, completas], 1)
        plano[:, completas] -= np.outer(t, coef[0]) + coef[1]
    for j in np.where(~completas & (finito.sum(axis=0) > 24))[0]:
        m = finito[:, j]
        b, a = np.polyfit(t[m], plano[m, j], 1)
        plano[:, j] -= b * t + a
    return anom.copy(data=plano.reshape(vals.shape)).transpose(*dims)


# --- Indices hasta 2100 -------------------------------------------------
#
# ONI: c2.oni_index tal cual (bases moviles de 30 anios del CPC). Con
# datos hasta 2100 la ultima base es 2071-2100, de modo que el
# calentamiento medio se va restando y los eventos se miden respecto del
# estado medio de su epoca (asi se calcula operativamente).
#
# ICEN: c2.icen_base_period congela la base en 1991-2020 desde 2011
# (Tabla 1 de la Nota Tecnica ENFEN). Hacia 2100 eso convertiria todo el
# calentamiento en "anomalia" (ICEN > 0.5 casi permanente). Aca se sigue
# el mismo patron de quinquenios sin el tope, igual que hace el CPC con
# el ONI.

def icen_base_period_sin_tope(year, data_start, data_end):
    b = 1946 + 5 * ((year - 1946) // 5)
    b0, b1 = b - 15, b + 14
    if b1 > data_end:
        b0, b1 = data_end - 29, data_end
    if b0 < data_start:
        b0, b1 = data_start, data_start + 29
    return b0, b1


def icen_index(nino12_da):
    return c2.rolling3(c2.anomaly_bloques(nino12_da, icen_base_period_sin_tope))


def oni_index(nino34_da):
    return c2.oni_index(nino34_da)


def roni_index(nino34_da, tropical_da, ref=REF):
    """RONI con base fija 'ref' (1985-2014, la misma de E2). Difiere de
    c2.roni_index en un solo punto: el factor de escala que iguala la
    varianza a la del Nino3.4 suavizado se calcula SOLO en la base, no
    en toda la serie. En E2 da igual (la serie es la base); hasta 2100,
    calcularlo con toda la serie mezclaria el cambio futuro de
    varianza dentro de la normalizacion y lo borraria en parte."""
    r0, r1 = ref
    a34 = c2.anomaly(nino34_da, c2.climatology(nino34_da, r0, r1))
    atr = c2.anomaly(tropical_da, c2.climatology(tropical_da, r0, r1))
    orig, raw = c2.rolling3(a34), c2.rolling3(a34 - atr)
    o = orig.sel(time=slice(f"{r0}", f"{r1}"))
    r = raw.sel(time=slice(f"{r0}", f"{r1}"))
    return raw * float(o.std(ddof=1, skipna=True) / r.std(ddof=1, skipna=True))


def indice_base_fija(da, ref=REF):
    """Rolling 3m de la anomalia respecto de la climatologia fija 'ref'
    (sin quitar el calentamiento). Variantes ONIfija/ICENfija: muestran
    cuanto de la "mayor ocurrencia" de eventos es solo el aumento del
    estado medio."""
    return c2.rolling3(c2.anomaly(da, c2.climatology(da, *ref)))


def xr_a_df(variables):
    """{nombre: DataArray con las mismas dims} -> DataFrame largo, sin
    las coordenadas auxiliares (model, seleccionado)."""
    d = xr.Dataset(variables)
    d = d.drop_vars([c for c in d.coords if c not in d.dims])
    return d.to_dataframe().reset_index()


def agregar_modelo(df, ds):
    """Antepone modelo y seleccionado (coords de series_cajas) a un
    DataFrame con columna number."""
    info = pd.DataFrame({"number": ds.number.values, "modelo": ds.model.values,
                         "seleccionado": ds.seleccionado.values})
    return info.merge(df, on="number")


def find_indices_csv(escenario):
    path = E3_DIR / f"indices_enso_{escenario}_{ANIO_INICIO}-{ANIO_FIN}.csv"
    if not path.exists():
        sys.exit(f"Falta {path}. Correr antes q06_indices_futuros.py.")
    return path


def silenciar_nan():
    """Los puntos de tierra (todo NaN) generan avisos de numpy al
    promediar, y scipy (SmallSampleWarning, subclase de RuntimeWarning)
    al pedir asimetria/curtosis de una serie vacia; no son errores."""
    warnings.filterwarnings("ignore", category=RuntimeWarning)
