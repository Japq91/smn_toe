#!/usr/bin/env python3
"""Paso q08 del calculo de E3: cambio en la ocurrencia y las
caracteristicas de los eventos calidos entre la referencia (1985-2014)
y cada periodo futuro, por modelo, escenario e indice.

Metricas por periodo (ref, P1, P2), a partir de los eventos de q07
(asignados por la fecha del pico) y de los indices de q06:

  n_eventos, frec_siglo     numero de eventos y tasa por 100 anios
  dur_media, mag_media, mag_max
  n_moderado_mas            eventos con categoria oficial moderado o mayor
  n_fuerte_mas              fuerte o mayor (ONI/RONI: fuerte, muy_fuerte;
                            ICEN: fuerte, extraordinario)
  n_extremo_rel             categoria relativa "extremo" (pico >= 2 sigma
                            de la referencia)
  frac_meses_umbral         fraccion de meses del periodo con el indice
                            sobre el umbral de inicio, sin exigir duracion
                            (en ONIfija/ICENfija mide cuanto del tiempo
                            se vive en "condiciones calidas" de hoy).
                            En esas variantes n_eventos BAJA hacia P2:
                            el indice queda sobre el umbral casi todo
                            el tiempo y los eventos se funden en uno
                            solo muy largo; la metrica que sirve ahi es
                            esta, no la frecuencia.
  razon_frec                frec_siglo(P) / frec_siglo(ref)
  n_costero, n_extendido,   eventos por tipo (q07; solo ICEN: costero y
  n_central, frac_costero   extendido; solo ONI: central y extendido).
                            frac_costero = n_costero / n_eventos del ICEN

Pruebas de cambio (P frente a ref, solo ONI, RONI e ICEN): las mismas
tres de p10 de E2 (scripts_e2/p10_pruebas_eventos.py, se importan sus
funciones), con la referencia del mismo modelo en el lugar de ERSSTv5:
razon de verosimilitud de Poisson (frecuencia), Anderson-Darling
(duracion) y prueba G del mes del pico (estacionalidad), y Holm sobre
las tres. Con ~6-12 eventos por periodo de 30 anios la potencia es baja:
la mayoria de los modelos no va a mostrar cambios significativos por si
solos, y la conclusion sale del conjunto (q10: cuantos modelos aumentan,
mediana multimodelo). Las variantes fijas no se prueban: su aumento
de frecuencia es en buena parte el calentamiento medio, que ya mide q02.

Permutaciones: N_PERM = 1999 (en E2, 9999). Alcanza para resolver
p = 0.05/3 tras Holm y deja la corrida en unos minutos con 480 pruebas.

Salida: data/processed/e3/cambio_eventos_ref1985-2014.csv -- una fila
por (escenario, indice, modelo, periodo).

Uso: python3 scripts_e3/q08_cambio_eventos.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3
import p10_pruebas_eventos as p10  # scripts_e2/ (via common_e3)
from q07_eventos_futuros import INDICES, config_umbral

INDICES_PRUEBA = ["ONI", "RONI", "ICEN"]
N_PERM = 1999
SEED = 0
ALFA = p10.ALFA
p10.N_PERM = N_PERM  # anderson_darling y g_estacionalidad leen el global del modulo

MODERADO_MAS = {"moderado", "fuerte", "muy_fuerte", "extraordinario"}
FUERTE_MAS = {"fuerte", "muy_fuerte", "extraordinario"}


# Caja de la que sale cada indice: define los meses con dato del periodo.
CAJA_INDICE = {"ONI": "nino34", "ONIfija": "nino34", "RONI": "nino34", "ICEN": "nino12", "ICENfija": "nino12"}


def metricas_periodo(ev, serie, indice, periodo, meses_dato):
    """meses_dato: meses del periodo con TSM en la caja (q01). Es el
    tiempo de observacion para la frecuencia y la prueba de Poisson. No se
    usa la cantidad de meses con indice porque la media movil centrada de
    3 meses deja sin valor 2100-12 (le falta 2101-01): P2 quedaria con
    359 meses y la frecuencia subiria 0.3 % sin que cambie el numero de
    eventos (razon 1.003 con los mismos eventos, contada como aumento).
    Los modelos que no tienen 2100 (CAMS-CSM1-0, IITM-ESM) siguen con
    sus 348 meses reales."""
    y0, y1 = c3.PERIODOS[periodo]
    s = serie.loc[f"{y0}":f"{y1}"].dropna()
    siglos = meses_dato / 1200
    cfg = config_umbral(indice)
    sd = s.round(cfg["redondeo"]) if "redondeo" in cfg else s
    sobre = (sd > cfg["inicio"]) if cfg.get("estricto") else (sd >= cfg["inicio"])
    return {
        "n_eventos": len(ev),
        "siglos": siglos,
        "frec_siglo": len(ev) / siglos if siglos else np.nan,
        "dur_media": ev["duracion_meses"].mean(),
        "mag_media": ev["magnitud_pico"].mean(),
        "mag_max": ev["magnitud_pico"].max(),
        "n_moderado_mas": int(ev["categoria_oficial"].isin(MODERADO_MAS).sum()),
        "n_fuerte_mas": int(ev["categoria_oficial"].isin(FUERTE_MAS).sum()),
        "n_extremo_rel": int((ev["categoria_relativa"] == "extremo").sum()),
        "frac_meses_umbral": float(sobre.mean()) if len(s) else np.nan,
        **tipos(ev, indice),
    }


def tipos(ev, indice):
    """Conteo por tipo de evento (q07), solo para ONI e ICEN."""
    out = {"n_costero": np.nan, "n_extendido": np.nan, "n_central": np.nan, "frac_costero": np.nan}
    if indice in ("ONI", "ICEN"):
        n = ev["tipo"].value_counts()
        out["n_extendido"] = int(n.get("extendido", 0))
        if indice == "ICEN":
            out["n_costero"] = int(n.get("costero", 0))
            out["frac_costero"] = out["n_costero"] / len(ev) if len(ev) else np.nan
        else:
            out["n_central"] = int(n.get("central", 0))
    return out


def pruebas(ev_p, ev_ref, m_p, m_ref, rng):
    """Frecuencia, duracion y estacionalidad de P frente a ref. Las de
    distribucion necesitan al menos 2 eventos en cada periodo."""
    out = {}
    out["G_frec"], out["p_frec"] = p10.lrt_poisson(m_p["n_eventos"], m_p["siglos"],
                                                   m_ref["n_eventos"], m_ref["siglos"])
    if len(ev_p) >= 2 and len(ev_ref) >= 2:
        out["A2_dur"], out["p_dur"] = p10.anderson_darling(ev_p["duracion_meses"].to_numpy(),
                                                           ev_ref["duracion_meses"].to_numpy(), rng)
        out["G_est"], out["p_est"] = p10.g_estacionalidad(ev_p["fecha_pico"].dt.month.to_numpy(),
                                                          ev_ref["fecha_pico"].dt.month.to_numpy(), rng)
    else:
        out.update(A2_dur=np.nan, p_dur=np.nan, G_est=np.nan, p_est=np.nan)
    ps = [out[f"p_{t}"] for t in p10.PRUEBAS]
    validos = [i for i, p in enumerate(ps) if np.isfinite(p)]
    ajust = p10.holm([ps[i] for i in validos])
    for t in p10.PRUEBAS:
        out[f"pholm_{t}"] = np.nan
    for k, i in enumerate(validos):
        out[f"pholm_{p10.PRUEBAS[i]}"] = ajust[k]
    out["cambios"] = ";".join(t for t in p10.PRUEBAS if out[f"pholm_{t}"] < ALFA)
    return out


def main():
    rng = np.random.default_rng(SEED)
    sel = c3.seleccion_e2()
    filas = []
    tos = c3.series_cajas().tos
    for esc in c3.ESCENARIOS:
        ind = pd.read_csv(c3.find_indices_csv(esc), index_col="time", parse_dates=True)
        path_ev = c3.E3_DIR / f"eventos_{esc}_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.csv"
        if not path_ev.exists():
            sys.exit(f"Falta {path_ev}. Correr antes q07_eventos_futuros.py.")
        eventos = pd.read_csv(path_ev, parse_dates=["inicio", "fin", "fecha_pico"])
        for indice in INDICES:
            print(f"  {esc} {indice} ...", file=sys.stderr)
            for number in sel.index:
                serie = ind[f"{number}_{indice}"]
                ev = eventos[(eventos.indice == indice) & (eventos.number == number)]
                ev_por = {p: ev[ev.periodo == p] for p in c3.PERIODOS}
                caja = tos.sel(number=number, escenario=esc, caja=CAJA_INDICE[indice])
                m = {p: metricas_periodo(ev_por[p], serie, indice, p,
                                         int(c3.recorte(caja, p).notnull().sum()))
                     for p in c3.PERIODOS}
                for p in c3.PERIODOS:
                    fila = {"escenario": esc, "indice": indice, "number": number,
                            "modelo": sel.loc[number, "modelo"],
                            "seleccionado": bool(sel.loc[number, "seleccionado"]),
                            "periodo": p, "anios": c3.etiqueta_periodo(p), **m[p]}
                    if p != "ref":
                        fr = m["ref"]["frec_siglo"]
                        fila["razon_frec"] = m[p]["frec_siglo"] / fr if fr else np.nan
                        if indice in INDICES_PRUEBA:
                            fila.update(pruebas(ev_por[p], ev_por["ref"], m[p], m["ref"], rng))
                    filas.append(fila)

    df = pd.DataFrame(filas)
    path = c3.E3_DIR / f"cambio_eventos_ref{c3.etiqueta_periodo('ref')}.csv"
    df.to_csv(path, index=False, float_format="%.6g")
    print(f"Listo: {path} ({len(df)} filas)", file=sys.stderr)

    fut = df[df.periodo != "ref"]
    tabla = fut.groupby(["escenario", "indice", "periodo"]).agg(
        frec_mediana=("frec_siglo", "median"), modelos_aumentan=("razon_frec", lambda x: int((x > 1).sum())),
        cambio_signif=("cambios", lambda x: int(x.fillna("").str.len().gt(0).sum())))
    ref = df[df.periodo == "ref"].groupby(["escenario", "indice"])["frec_siglo"].median().rename("frec_ref")
    print("Eventos por siglo, 40 modelos (mediana) y modelos que aumentan / con cambio significativo:\n"
          + tabla.join(ref).round(1).to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
