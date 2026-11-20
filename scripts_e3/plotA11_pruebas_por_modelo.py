#!/usr/bin/env python3
"""plotA11 -- Figura A11 del informe E3: figures/e3/e3_A11_pruebas_por_modelo.png

Estacionalidad de los eventos: porcentaje de los eventos con pico en cada mes,
juntando los eventos de los modelos del grupo, en ref y en P1 (fila 1) o P2
(fila 2) de cada escenario, para ONI, RONI e ICEN (columnas). Es la propiedad que
compara la prueba G de q08 y la única de las tres sin otra figura (la frecuencia
está en la Figura 8 y la duración en la Figura 9).

El conteo de modelos con cambio significativo en cada prueba por modelo (q08,
Holm sobre frecuencia, duración y estacionalidad) va como cuadro en el Anexo del
informe; este script lo imprime en formato LaTeX (tabla_conteos) para copiarlo.

Entrada: cambio_eventos_ref<ref>.csv (q08), eventos_<esc>_1850-2100.csv (q07) (data/processed/e3/)
Salida: figures/e3/e3_A11_pruebas_por_modelo.png

Uso: python3 scripts_e3/plotA11_pruebas_por_modelo.py   (o bash rune3plot.sh A11)
     E3_GRUPO=40 python3 scripts_e3/plotA11_pruebas_por_modelo.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)

ALFA = 0.05
PRUEBAS = [("frec", "frecuencia"), ("dur", "duración"), ("est", "estacionalidad")]


@cache
def eventos(esc):
    return leer(f"eventos_{esc}_{c3.ANIO_INICIO}-{c3.ANIO_FIN}.csv", ("inicio", "fin", "fecha_pico"))


def matriz_conteos(ev):
    """Filas (índice, prueba), columnas (escenario, periodo): número de modelos del
    grupo con pholm_<prueba> < ALFA."""
    filas = [(ind, t) for ind in INDICES for t, _ in PRUEBAS]
    cats = cats_fut()
    m = np.zeros((len(filas), len(cats)), int)
    for i, (ind, t) in enumerate(filas):
        for j, (esc, per) in enumerate(cats):
            d = ens(ev, indice=ind, escenario=esc, periodo=per)
            d = d[d.number.isin(SEL)]
            m[i, j] = int((d[f"pholm_{t}"] < ALFA).sum())
    return filas, cats, m


def tabla_conteos(filas, cats, m):
    """Cuadro LaTeX (booktabs) con el número de modelos con cambio significativo."""
    nom = dict(PRUEBAS)
    lin = [" & ".join(["Índice", "Propiedad"] + [etiqueta_cat(e, p).replace("\n", " ") for e, p in cats]) + r" \\"]
    for i, (ind, t) in enumerate(filas):
        if i and i % len(PRUEBAS) == 0:
            lin.append(r"\midrule")
        lin.append(" & ".join([ind if i % len(PRUEBAS) == 0 else "", nom[t]] + [str(v) for v in m[i]]) + r" \\")
    return "\n".join(lin)


def panel_estacionalidad(ax, ind, per_fut):
    """Dibuja las curvas y devuelve el máximo, para fijar el eje común."""
    meses = np.arange(1, 13)
    tope = 0
    series = [("ref", ESCS[0], COL_PER["ref"], NOM_HIST, 2.4)] + \
             [(per_fut, e, COL_ESC[e], f"{per_fut} {NOM_ESC[e]}", 1.4) for e in ESCS]
    for per, esc, col, lab, lw in series:
        ev = eventos(esc)
        d = ev[(ev.indice == ind) & (ev.periodo == per) & ev.number.isin(SEL)]
        frac = d.fecha_pico.dt.month.value_counts().reindex(meses, fill_value=0) / max(len(d), 1) * 100
        ax.plot(meses, frac.to_numpy(), "-o", ms=3, lw=lw, color=col, label=f"{lab} ({len(d)} ev.)", zorder=3)
        tope = max(tope, frac.max())
    ax.set_xticks(meses, MESES)
    ax.set_xlim(0.5, 12.5)
    ax.grid(axis="y", color="0.9", lw=0.6)
    ax.legend(frameon=False, fontsize=7, loc="upper center")
    return tope


def main():
    filas, cats, m = matriz_conteos(cambio_ev())
    print("Cuadro de conteos (LaTeX):\n" + tabla_conteos(filas, cats, m), file=sys.stderr)
    fig, axs = plt.subplots(len(FUTS), len(INDICES), figsize=(10, 6.6), layout="constrained", sharex=True, sharey=True)
    topes = []
    for i, per in enumerate(FUTS):
        for j, ind in enumerate(INDICES):
            topes.append(panel_estacionalidad(axs[i, j], ind, per))
            p0.titulo_panel(axs[i, j], LETRAS[len(INDICES) * i + j], f"{ind}, {NOM_PER[per]}")
        axs[i, 0].set_ylabel("eventos con pico\nen el mes [%]")
    axs[0, 0].set_ylim(0, max(topes) * 1.3)   # espacio para la leyenda
    fig.suptitle(f"Mes del pico de los eventos cálidos: todos los eventos de los {len(SEL)} modelos")
    guardar(fig, "A11_pruebas_por_modelo")


if __name__ == "__main__":
    main()
