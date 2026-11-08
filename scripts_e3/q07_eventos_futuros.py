#!/usr/bin/env python3
"""Paso q07 del calculo de E3: eventos calidos 1850-2100 por modelo,
escenario e indice (ONI, RONI, ICEN, ONIfija, ICENfija), con los
mismos criterios de E2 (scripts_e2/p07_eventos.py, se importan sus
funciones y umbrales, no se copian):

  - deteccion con el umbral OFICIAL: ONI/RONI >= 0.5 durante >= 5
    meses; ICEN > 0.5 (2 decimales) durante >= 3 meses (ENFEN 01-2024).
    Las variantes de base fija usan el umbral de su indice.
  - categoria_oficial sobre el pico (debil ... muy_fuerte/extraordinario).
  - categoria_relativa sobre pico / sigma (Shin et al. 2022), con una
    diferencia respecto de E2: sigma es la del indice en la referencia
    1985-2014, no la de toda la serie. Con datos hasta 2100 la sigma de
    toda la serie ya incluye el cambio futuro; fijarla en la referencia
    hace que "extremo" signifique lo mismo en todos los periodos.

Cada evento se asigna al periodo (ref, P1, P2) de su pico; los que
caen fuera de los tres (ej. 2015-2035) quedan con periodo vacio pero se
conservan, para las figuras de series completas.

Tipo de evento (solo ONI e ICEN, los dos indices operativos en Peru):
se cruzan los eventos de ambos indices del mismo modelo y escenario, y
dos eventos se consideran el mismo episodio si sus intervalos
[inicio, fin] se superponen al menos un mes.
  costero    evento ICEN sin evento ONI simultaneo (El Nino costero:
             calentamiento frente a Peru sin El Nino en el Pacifico
             central, como 1925 o 2017)
  extendido  evento ICEN con evento ONI simultaneo (o viceversa): El
             Nino de todo el Pacifico oriental-central (1982-83, 1997-98)
  central    evento ONI sin evento ICEN simultaneo (calentamiento solo
             en el Pacifico central, sin senal costera)
Es la forma de saber si el cambio climatico altera la proporcion de
eventos que llegan a la costa, que es lo que determina el impacto en
Peru. Para los demas indices, tipo queda vacio.

Lee indices_enso_<escenario>_1850-2100.csv (q06).

Salida: data/processed/e3/eventos_<escenario>_1850-2100.csv -- una
fila por evento: indice, number, inicio, fin, fecha_pico,
duracion_meses, magnitud_pico, categoria_oficial, categoria_relativa,
periodo, tipo.

Uso: python3 scripts_e3/q07_eventos_futuros.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3
import p07_eventos as p07  # scripts_e2/ ya esta en sys.path (common_e3)

INDICES = ["ONI", "RONI", "ICEN", "ONIfija", "ICENfija"]


def config_umbral(indice):
    """Umbral oficial de E2; las variantes 'fija' usan el de su indice."""
    return p07.UMBRAL_OFICIAL[indice.replace("fija", "")]


def eventos_indice(df, indice):
    cfg = config_umbral(indice)
    numbers = [c.rsplit("_", 1)[0] for c in df.columns if c.endswith(f"_{indice}")]
    filas = []
    for number in numbers:
        serie = df[f"{number}_{indice}"].dropna()
        y0, y1 = c3.REF
        sigma_ref = float(serie.loc[f"{y0}":f"{y1}"].std(ddof=1))
        serie_det = serie.round(cfg["redondeo"]) if "redondeo" in cfg else serie
        for ev in p07.detect_events(serie_det, cfg["inicio"], cfg["duracion_min"], cfg.get("estricto", False)):
            ev.update(indice=indice, number=number,
                      categoria_oficial=p07.categorize(ev["magnitud_pico"], cfg["categorias"],
                                                       cfg.get("redondeo", 1), cfg.get("intervalo", "cerrado")),
                      categoria_relativa=p07.categorize(ev["magnitud_pico"] / sigma_ref,
                                                        p07.UMBRAL_RELATIVO_SIGMAS),
                      periodo=c3.periodo_de_fecha(ev["fecha_pico"]))
            filas.append(ev)
    return filas


def asignar_tipo(ev):
    """Columna 'tipo' (costero / extendido / central) para los eventos
    ONI e ICEN, segun haya o no un evento del otro indice superpuesto."""
    ev["tipo"] = None
    for number, g in ev.groupby("number"):
        oni = g[g.indice == "ONI"]
        icen = g[g.indice == "ICEN"]
        for idx, fila in icen.iterrows():
            solapa = ((oni.inicio <= fila.fin) & (oni.fin >= fila.inicio)).any()
            ev.at[idx, "tipo"] = "extendido" if solapa else "costero"
        for idx, fila in oni.iterrows():
            solapa = ((icen.inicio <= fila.fin) & (icen.fin >= fila.inicio)).any()
            ev.at[idx, "tipo"] = "extendido" if solapa else "central"
    return ev


def main():
    cols = ["indice", "number", "inicio", "fin", "fecha_pico", "duracion_meses", "magnitud_pico",
            "categoria_oficial", "categoria_relativa", "periodo", "tipo"]
    for esc in c3.ESCENARIOS:
        df = pd.read_csv(c3.find_indices_csv(esc), index_col="time", parse_dates=True)
        filas = []
        for indice in INDICES:
            filas += eventos_indice(df, indice)
        ev = asignar_tipo(pd.DataFrame(filas, columns=cols))
        path = c3.E3_DIR / f"eventos_{esc}_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.csv"
        ev.to_csv(path, index=False, float_format="%.4f")
        conteo = ev[ev.periodo.notna()].groupby(["indice", "periodo"]).size().unstack()[list(c3.PERIODOS)]
        print(f"Listo: {path} ({len(ev)} eventos). Total de los 40 modelos por periodo:\n"
              + conteo.to_string(), file=sys.stderr)
        tipos = ev[ev.indice == "ICEN"].groupby(["periodo", "tipo"]).size().unstack()
        print("  Eventos ICEN por tipo (40 modelos):\n" + tipos.to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
