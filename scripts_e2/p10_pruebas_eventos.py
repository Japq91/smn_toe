#!/usr/bin/env python3
"""Paso p10 del calculo de E2: pruebas estadisticas del regimen de
eventos calidos de cada modelo frente a ERSSTv5 (filtro previo a la
seleccion por skill score).

Pregunta: ¿los eventos calidos del modelo son estadisticamente
distinguibles de los observados en frecuencia, duracion y
estacionalidad? Un modelo cuyo regimen de eventos no se puede
distinguir del observado pasa el filtro; los que pasan se ordenan
despues por S_final (p09). El corte final queda por definir.

Indices: RONI (Nino 3.4) e ICEN (Nino 1+2). El ONI no entra: comparte
casi todos sus eventos con el RONI, de modo que sus pruebas no serian
independientes y Nino 3.4 contaria dos veces.

Datos (todo sobre 1900-02 a 2014-11, la ventana comun de p01):
  - eventos_<INDICE>_<y0>-<y1>.csv (p07): una fila por evento, con
    duracion_meses y fecha_pico, para los 40 modelos y OBS (ERSSTv5).
  - indices_enso_<y0>-<y1>.csv (p01) + OBS recalculado: el numero de
    meses validos de cada serie, que da la longitud T del registro.

Tres pruebas por indice, una por propiedad (6 pruebas por modelo):

1. Frecuencia -- prueba de razon de verosimilitud para dos tasas de
   Poisson. Cada dataset aporta un solo dato: n eventos en T siglos.
   Se supone que los eventos ocurren como un proceso de Poisson con
   tasa lambda (eventos por siglo). Bajo H0 (misma tasa) el estimador
   de maxima verosimilitud comun es

       lambda0 = (n_m + n_o) / (T_m + T_o)

   y bajo H1 cada dataset tiene la suya, lambda_k = n_k / T_k. El
   estadistico es dos veces el logaritmo del cociente de verosimilitudes;
   con la verosimilitud de Poisson, L = prod (lambda T)^n e^(-lambda T) / n!,
   los terminos e^(-lambda T) se cancelan (sum lambda_k T_k = lambda0 sum T_k)
   y queda

       G = 2 * sum_k n_k * ln( n_k / (T_k * lambda0) ),   k = modelo, obs

   Por el teorema de Wilks, G ~ chi2 con 1 grado de libertad (2
   parametros bajo H1 menos 1 bajo H0). Anderson-Darling no aplica aqui:
   no hay una distribucion que comparar, solo un conteo.

2. Duracion -- Anderson-Darling de k muestras (Scholz y Stephens, 1987),
   con k = 2: compara la distribucion completa de las duraciones de los
   eventos del modelo con la de los observados, no solo la media. Con
   las dos muestras juntas (N = n_m + n_o) y su distribucion empirica
   H_N, el estadistico es

       A2 = 1/N * sum_i 1/n_i * sum_j (N F_ij - n_i H_j)^2 / (H_j (N - H_j))

   donde F_ij es el numero de valores de la muestra i que no superan el
   j-esimo valor distinto de la muestra conjunta. Es una distancia
   cuadratica entre las distribuciones acumuladas, ponderada por
   1 / (H (1 - H)), que da mas peso a las colas que Kolmogorov-Smirnov
   (importante aqui: los modelos fallan en la cola de eventos largos).
   Las duraciones son meses enteros con muchos empates, por lo que se
   usa la version de rangos medios de scipy y el valor p se obtiene por
   permutacion (N_PERM reasignaciones aleatorias de los eventos entre
   modelo y obs), sin depender de la aproximacion asintotica.

3. Estacionalidad -- prueba G (razon de verosimilitud multinomial) sobre
   el mes del pico. Tabla de contingencia de 2 filas (modelo, obs) x 12
   columnas (mes del pico). Bajo H0 ambos datasets reparten los picos
   con las mismas probabilidades por mes; las frecuencias esperadas son
   E_ij = (total fila i)(total columna j) / N, y

       G = 2 * sum_ij O_ij * ln( O_ij / E_ij )

   (las celdas con O_ij = 0 aportan 0). Asintoticamente G ~ chi2 con 11
   grados de libertad, pero con 30-40 eventos observados muchas celdas
   tienen E_ij < 5 y la aproximacion falla, asi que el valor p se
   obtiene por permutacion (N_PERM reasignaciones de los meses entre
   modelo y obs, que conservan los totales). Anderson-Darling no se usa
   aqui porque trata el mes como una escala lineal: diciembre y enero
   quedarian en extremos opuestos, cuando son meses vecinos.

Comparaciones multiples -- correccion de Holm (1979) por modelo. Con 6
pruebas a alfa = 0.05, la probabilidad de rechazar al menos una por
azar aunque el modelo sea igual a la observacion es 1 - 0.95^6 ~ 0.26.
Holm controla esa tasa (FWER) en alfa: se ordenan los 6 valores p de
menor a mayor, p(1) <= ... <= p(6), y el valor p ajustado es

    p_holm(j) = max_{l <= j} min(1, (6 - l + 1) * p(l))

El modelo pasa el filtro si ningun p_holm es menor que ALFA, es decir,
si p(1) >= ALFA / 6. Holm es uniformemente mas potente que Bonferroni
y no supone independencia entre las pruebas.

Supuestos y limites: los eventos de un mismo dataset se tratan como
independientes (estan separados por meses neutros, pero el ENOS tiene
memoria interanual); cada modelo es un solo miembro, de modo que parte
de las diferencias puede ser variabilidad interna de esa corrida. Con
pocos eventos las pruebas tienen poca potencia: no rechazar significa
"no distinguible con esta muestra", no "igual a la observacion".

    Scholz, F. W., & Stephens, M. A. (1987). K-sample Anderson-Darling
    tests. Journal of the American Statistical Association, 82(399),
    918-924. doi:10.1080/01621459.1987.10478517
    Holm, S. (1979). A simple sequentially rejective multiple test
    procedure. Scandinavian Journal of Statistics, 6(2), 65-70.
    Wilks, S. S. (1938). The large-sample distribution of the likelihood
    ratio for testing composite hypotheses. Annals of Mathematical
    Statistics, 9(1), 60-62. doi:10.1214/aoms/1177732360

Salida: pruebas_eventos_<y0>-<y1>.csv, una fila por modelo (M01..M40)
y una fila OBS con los valores observados (sin valores p). Columnas por
indice I (RONI, ICEN): n_eventos_I, siglos_I, frec_I [eventos/siglo],
G_frec_I, p_frec_I, dur_media_I [meses], A2_dur_I, p_dur_I, G_est_I,
p_est_I y los ajustados pholm_frec_I, pholm_dur_I, pholm_est_I; al
final, rechazadas (pruebas con p_holm < ALFA) y pasa_filtro.

Uso:
    python3 scripts_e2/p10_pruebas_eventos.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_e2 as c2

INDICES = ["RONI", "ICEN"]
PRUEBAS = ["frec", "dur", "est"]

# Nivel de significancia de la familia de pruebas de cada modelo (Holm).
ALFA = 0.05

# Permutaciones para los valores p de duracion y estacionalidad, y
# semilla, para reproducibilidad exacta entre corridas.
N_PERM = 9999
SEED = 0


def lrt_poisson(n_m, t_m, n_o, t_o):
    """Razon de verosimilitud de dos tasas de Poisson (punto 1 del
    docstring). Devuelve (G, p)."""
    lam0 = (n_m + n_o) / (t_m + t_o)
    g = sum(2 * n * np.log(n / (t * lam0)) for n, t in [(n_m, t_m), (n_o, t_o)] if n > 0)
    return g, stats.chi2.sf(g, df=1)


def anderson_darling(dur_m, dur_o, rng):
    """Anderson-Darling de 2 muestras con valor p por permutacion
    (punto 2 del docstring). Devuelve (A2, p)."""
    res = stats.anderson_ksamp([dur_m, dur_o], variant="midrank",
                               method=stats.PermutationMethod(n_resamples=N_PERM, random_state=rng))
    return res.statistic, res.pvalue


def g_meses(mes_m, mes_o):
    """Estadistico G de la tabla 2 x 12 de meses del pico."""
    o = np.vstack([np.bincount(mes_m - 1, minlength=12),
                   np.bincount(mes_o - 1, minlength=12)]).astype(float)
    e = o.sum(axis=1, keepdims=True) * o.sum(axis=0) / o.sum()
    m = o > 0
    return 2 * float(np.sum(o[m] * np.log(o[m] / e[m])))


def g_estacionalidad(mes_m, mes_o, rng):
    """Prueba G con valor p por permutacion (punto 3 del docstring).
    Devuelve (G, p)."""
    g0 = g_meses(mes_m, mes_o)
    todos, n_m = np.concatenate([mes_m, mes_o]), len(mes_m)
    mayores = 0
    for _ in range(N_PERM):
        rng.shuffle(todos)
        mayores += g_meses(todos[:n_m], todos[n_m:]) >= g0
    return g0, (mayores + 1) / (N_PERM + 1)


def holm(p):
    """Valores p ajustados de Holm (1979) para un vector de valores p."""
    p = np.asarray(p, dtype=float)
    k, orden = len(p), np.argsort(p)
    ajust = np.empty(k)
    acumulado = 0.0
    for j, idx in enumerate(orden):
        acumulado = max(acumulado, min(1.0, (k - j) * p[idx]))
        ajust[idx] = acumulado
    return ajust


def main():
    periodo = c2.indices_period()
    registro = c2.read_model_registry()
    modelos = [r["number"] for r in registro]
    rng = np.random.default_rng(SEED)

    print("Cargando indices (p01 + OBS) y eventos (p07) ...", file=sys.stderr)
    ind = c2.load_all_indices()
    filas = {n: {} for n in modelos + ["OBS"]}
    for i in INDICES:
        path = c2.E2_DIR / f"eventos_{i}_{periodo}.csv"
        if not path.exists():
            sys.exit(f"Falta {path}. Correr antes p07_eventos.py.")
        ev = pd.read_csv(path, parse_dates=["fecha_pico"])
        for n in modelos + ["OBS"]:
            d = ev[ev["number"] == n]
            siglos = ind[f"{n}_{i}"].notna().sum() / 1200
            filas[n].update({f"n_eventos_{i}": len(d), f"siglos_{i}": siglos,
                             f"frec_{i}": len(d) / siglos, f"dur_media_{i}": d["duracion_meses"].mean()})
        o = ev[ev["number"] == "OBS"]
        mes_o = o["fecha_pico"].dt.month.to_numpy()
        print(f"  {i}: OBS con {len(o)} eventos ({filas['OBS'][f'frec_{i}']:.1f}/siglo)", file=sys.stderr)
        for n in modelos:
            d = ev[ev["number"] == n]
            f = filas[n]
            f[f"G_frec_{i}"], f[f"p_frec_{i}"] = lrt_poisson(len(d), f[f"siglos_{i}"],
                                                             len(o), filas["OBS"][f"siglos_{i}"])
            f[f"A2_dur_{i}"], f[f"p_dur_{i}"] = anderson_darling(d["duracion_meses"].to_numpy(),
                                                                 o["duracion_meses"].to_numpy(), rng)
            f[f"G_est_{i}"], f[f"p_est_{i}"] = g_estacionalidad(d["fecha_pico"].dt.month.to_numpy(), mes_o, rng)

    df = pd.DataFrame.from_dict(filas, orient="index")
    df.index.name = "number"
    cols_p = [f"p_{t}_{i}" for i in INDICES for t in PRUEBAS]
    ajust = np.vstack([holm(df.loc[n, cols_p].to_numpy()) for n in modelos])
    for k, c in enumerate(cols_p):
        df.loc[modelos, c.replace("p_", "pholm_", 1)] = ajust[:, k]
    cols_h = [c.replace("p_", "pholm_", 1) for c in cols_p]
    df.loc[modelos, "rechazadas"] = [";".join(c.replace("pholm_", "") for c in cols_h if df.loc[n, c] < ALFA)
                                     for n in modelos]
    df.loc[modelos, "pasa_filtro"] = (df.loc[modelos, cols_h] >= ALFA).all(axis=1)

    orden_cols = []
    for i in INDICES:
        orden_cols += [f"n_eventos_{i}", f"siglos_{i}", f"frec_{i}", f"G_frec_{i}", f"p_frec_{i}",
                       f"dur_media_{i}", f"A2_dur_{i}", f"p_dur_{i}", f"G_est_{i}", f"p_est_{i}"]
    df = df[orden_cols + cols_h + ["rechazadas", "pasa_filtro"]]

    sin = (df.loc[modelos, cols_p] < ALFA).sum()
    print(f"  Rechazos sin corregir (p < {ALFA}): " + ", ".join(f"{c[2:]}={v}" for c, v in sin.items()),
          file=sys.stderr)
    pasan = df.index[df["pasa_filtro"] == True].tolist()  # noqa: E712 (la fila OBS es NaN)
    print(f"  Pasan el filtro (Holm, alfa={ALFA}): {len(pasan)} de {len(modelos)} -> {', '.join(pasan)}",
          file=sys.stderr)

    out = c2.E2_DIR / f"pruebas_eventos_{periodo}.csv"
    df.to_csv(out, float_format="%.6g")
    print(f"Listo: {out}")


if __name__ == "__main__":
    main()
