#!/usr/bin/env python3
"""Paso q10 del calculo de E3: resumen multimodelo de los cambios de
q02 (estado medio), q04 (ciclo anual), q05 (variabilidad), q08
(eventos) y q09 (espectro), para los cuatro conjuntos de
common_e3.grupos(): 15 (principal, seleccion de E2), 40 (contraste), y
las dos pruebas de sensibilidad que recomienda el informe de E2: 11 (los
15 sin los de ICEN mas debil) y 7 (criterio anterior S >= 0.9).

Por (grupo, escenario, periodo, variable, caja o indice):
  n_modelos, media, mediana, p10, p90, minimo, maximo
  n_aumentan    modelos con cambio > 0 (en razon_frec, > 1)
  acuerdo_signo fraccion de modelos que coinciden con el signo de la
                mediana -- criterio del IPCC AR6 (Atlas, enfoque
                simple): >= 0.8 se considera un cambio robusto en signo.
                NaN si la mediana es igual al valor neutro
  p_wilcoxon    prueba de rangos con signo de Wilcoxon sobre los modelos
                del grupo: en las variables de cambio, si la mediana
                difiere del valor neutro; en las de nivel (P1/P2), si
                difieren de ref, pareando cada modelo consigo mismo. Es
                la significancia del cambio multimodelo: complementa a
                las pruebas por modelo de q08, que tienen poca potencia
  pholm_wilcoxon p_wilcoxon ajustado por Holm (1979). La familia es, en
                cada tabla (grupo, escenario, periodo), el subconjunto
                FAMILIA_HOLM (30 pruebas: las que pide el TdR mas
                duracion, fraccion costera, RONI e indices fijos); fuera
                de ella queda NaN. Controla la probabilidad de al menos
                un falso positivo en la familia (FWER) en ALFA. Limite:
                el p exacto minimo de Wilcoxon con n modelos es 2/2^n
                (0.016 con 7, 0.001 con 11): por 30 da 0.47 y 0.03, asi
                que en el grupo 7 ninguna prueba puede ser significativa
                y en el 11 solo las de p minimo
  signif        pholm_wilcoxon < ALFA (False fuera de FAMILIA_HOLM)

Es la tabla que alimenta los cuadros del informe; las figuras pueden
leer directo los CSV de cada paso si necesitan los valores por modelo.

Salida: data/processed/e3/resumen_multimodelo_ref1985-2014.csv

Uso: python3 scripts_e3/q10_resumen_multimodelo.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e3 as c3
import p10_pruebas_eventos as p10  # scripts_e2/ (via common_e3): holm()

REF = c3.etiqueta_periodo("ref")
ALFA = 0.05

# (archivo, columna con la caja o el indice, variables)
FUENTES = [
    (f"estado_medio_ref{REF}.csv", "caja", ["delta", "delta_relativo"]),
    (f"ciclo_anual_amplitud_ref{REF}.csv", "caja", ["amplitud", "delta_amplitud"]),
    (f"variabilidad_cajas_ref{REF}.csv", "caja",
     ["sigma_3m", "delta_sigma_pct", "delta_sigma_3m_pct", "asimetria", "curtosis"]),
    (f"cambio_eventos_ref{REF}.csv", "indice",
     ["frec_siglo", "razon_frec", "dur_media", "mag_media", "n_fuerte_mas", "n_extremo_rel",
      "frac_meses_umbral", "n_costero", "n_extendido", "n_central", "frac_costero"]),
    (f"espectro_resumen_ref{REF}.csv", "indice", ["periodo_pico_anios", "frac_banda_enso"]),
]
# Variables de cambio y su valor neutro (separa aumento de disminucion):
# se resumen solo en P1/P2, con n_aumentan y acuerdo_signo. Las demas son
# de nivel (asimetria, frec_siglo, ...): se resumen tambien en ref, para
# comparar, sin estadisticos de signo.
NEUTRO = {"delta": 0, "delta_relativo": 0, "delta_amplitud": 0, "delta_sigma_pct": 0,
          "delta_sigma_3m_pct": 0, "razon_frec": 1}
# Variables de nivel sin prueba P frente a ref porque duplicarian la de su
# variable de cambio (amplitud P - ref es exactamente delta_amplitud) e
# inflarian la familia de Holm.
SIN_PRUEBA = {"amplitud"}
# Familia de Holm: solo las pruebas que responden la actividad (c) del TdR
# (estado medio, variabilidad, frecuencia, intensidad y ocurrencia de
# eventos extremos en Nino 3.4 y Nino 1+2 con ONI e ICEN), mas duracion,
# fraccion costera, RONI y los indices de base fija. El resto conserva
# p_wilcoxon como referencia, pero sin Holm ni signif: se lee por mediana
# y acuerdo_signo. Una familia mas chica hace la correccion menos severa.
_INDICES = {"ONI", "RONI", "ICEN", "ONIfija", "ICENfija"}
FAMILIA_HOLM = {
    "delta": {"nino34", "nino12"},
    "delta_sigma_3m_pct": {"nino34", "nino12"},
    **{v: _INDICES for v in ("razon_frec", "mag_media", "n_fuerte_mas", "dur_media",
                             "frac_meses_umbral")},
    "frac_costero": {"ICEN"},
}


def wilcoxon(x, y=None):
    """Valor p de Wilcoxon (dos colas); NaN si no hay diferencias."""
    d = (x - y).dropna() if y is not None else x.dropna()
    if len(d) < 5 or (d == 0).all():
        return np.nan
    return float(stats.wilcoxon(d).pvalue)


def resumir(x, neutro, x_ref=None):
    x = x.dropna()
    if x.empty:
        return {}
    med = x.median()
    if neutro is not None:
        p = wilcoxon(x - neutro)
    elif x_ref is not None:
        p = wilcoxon(x, x_ref.reindex(x.index))
    else:
        p = np.nan
    signo_med = np.sign(med - neutro) if neutro is not None else np.nan
    return {
        "n_modelos": len(x), "media": x.mean(), "mediana": med,
        "p10": x.quantile(0.1), "p90": x.quantile(0.9), "minimo": x.min(), "maximo": x.max(),
        "n_aumentan": int((x > neutro).sum()) if neutro is not None else np.nan,
        # mediana igual al neutro (ej. razon_frec = 1): no hay signo con el
        # que coincidir, el acuerdo queda indefinido
        "acuerdo_signo": float((np.sign(x - neutro) == signo_med).mean())
                         if neutro is not None and signo_med != 0 else np.nan,
        "p_wilcoxon": p,
    }


def main():
    filas = []
    for archivo, col_clave, variables in FUENTES:
        path = c3.E3_DIR / archivo
        if not path.exists():
            sys.exit(f"Falta {path}. Correr antes los pasos q02-q09.")
        df = pd.read_csv(path).set_index("number")
        for grupo, numeros in c3.grupos().items():
            sub = df[df.index.isin(numeros)]
            for (esc, periodo, clave), g in sub.groupby(["escenario", "periodo", col_clave]):
                ref = sub[(sub.escenario == esc) & (sub.periodo == "ref") & (sub[col_clave] == clave)]
                for v in variables:
                    neutro = NEUTRO.get(v)
                    if neutro is not None and periodo == "ref":
                        continue
                    x_ref = ref[v] if (neutro is None and periodo != "ref" and not ref.empty
                                       and v not in SIN_PRUEBA) else None
                    r = resumir(g[v], neutro, x_ref)
                    if r:
                        filas.append({"grupo": grupo, "escenario": esc, "periodo": periodo,
                                      "variable": v, "caja_indice": clave, **r})

    out = pd.DataFrame(filas)
    out["pholm_wilcoxon"] = np.nan
    en_familia = [c in FAMILIA_HOLM.get(v, ()) for v, c in zip(out.variable, out.caja_indice)]
    for _, g in out[en_familia].groupby(["grupo", "escenario", "periodo"]):
        g = g["p_wilcoxon"].dropna()
        if len(g):
            out.loc[g.index, "pholm_wilcoxon"] = p10.holm(g.to_numpy())
    out["signif"] = out["pholm_wilcoxon"] < ALFA
    orden = {**{p: i for i, p in enumerate(c3.PERIODOS)}, **{g: i for i, g in enumerate(c3.grupos())}}
    out = out.sort_values(["grupo", "variable", "caja_indice", "escenario", "periodo"],
                          key=lambda s: s.map(orden) if s.name in ("periodo", "grupo") else s)
    path = c3.E3_DIR / f"resumen_multimodelo_ref{REF}.csv"
    out.to_csv(path, index=False, float_format="%.6g")   # %.6g: los p de ~1e-5 no se redondean a 0
    print(f"Listo: {path} ({len(out)} filas)", file=sys.stderr)

    ver = out[(out.grupo == "15") & (out.variable.isin(["delta", "delta_sigma_3m_pct"]))
              & (out.caja_indice != "tropical")]
    print("Conjunto de 15 modelos:\n" + ver[["variable", "caja_indice", "escenario", "periodo", "mediana",
                                             "p10", "p90", "acuerdo_signo", "p_wilcoxon", "pholm_wilcoxon"]].round(2).to_string(index=False),
          file=sys.stderr)


if __name__ == "__main__":
    main()
