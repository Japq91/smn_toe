#!/usr/bin/env python3
"""plotA02 -- Figura A2 del informe E3: figures/e3/e3_A02_ciclo_anual.png

Ciclo anual de la TSM en Niño 3.4 y Niño 1+2: cajas por mes con la distribución
entre los modelos del grupo, en ref (gris) y en P1/P2 con SSP2-4.5 y SSP5-8.5. Número
bajo cada caja: mediana del cambio respecto de ref.

Entrada: ciclo_anual_ref<ref>.csv (q04) (data/processed/e3/)
Salida: figures/e3/e3_A02_ciclo_anual.png

Uso: python3 scripts_e3/plotA02_ciclo_anual.py   (o bash rune3plot.sh A02)
     E3_GRUPO=40 python3 scripts_e3/plotA02_ciclo_anual.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    escs = ESCS_TDR
    cic = ciclo()
    cic = cic[cic.number.isin(SEL)]
    faltan = [e for e in escs if e not in set(cic.escenario)]
    if faltan:
        print(f"Sin datos para {faltan}: agregarlos a common_e3.ESCENARIOS y correr ./rune3.sh q01 q04",
              file=sys.stderr)
    escs = [e for e in escs if e not in faltan]
    # 'historical' = la referencia, la misma en todos los escenarios: se toma una vez
    hist = cic[(cic.periodo == "ref") & (cic.escenario == cic.escenario.iloc[0])]
    series = [("historical", hist)] + [(e, cic[cic.escenario == e]) for e in escs]
    ancho = 0.8 / len(series)
    desp = (np.arange(len(series)) - (len(series) - 1) / 2) * ancho
    fig, axs = plt.subplots(2, 2, figsize=(10, 6), layout="constrained", sharex=True, sharey="row")
    for i, caja in enumerate(CAJAS):
        for j, per in enumerate(FUTS):
            ax = axs[i, j]
            for k, (esc, d) in enumerate(series):
                d = d[d.caja == caja]
                if esc != "historical":
                    d = d[d.periodo == per]
                por_mes = [d[d.mes == m] for m in range(1, 13)]
                etiq = [x["delta"].median() for x in por_mes] if esc != "historical" else None
                dibujar_cajas(ax, [x["tsm"].dropna().to_numpy() for x in por_mes], np.arange(1, 13) + desp[k], esc,
                              ancho, etiq)
            separadores(ax, 12)
            ax.set_xticks(range(1, 13), MESES)
            if j == 0:
                ax.set_ylabel(f"TSM {NOM_CAJA[caja]} [°C]")
            p0.titulo_panel(ax, LETRAS[2 * i + j], f"{NOM_PER[per]}")
        margen_etiquetas(axs[i, 0])     # espacio para los numeros bajo las cajas (eje compartido en la fila)
    leyenda_cajas(fig, series, extra="número bajo cada caja\nmediana del cambio respecto de ref [°C]")
    fig.suptitle(f"Ciclo anual de la TSM\ndistribución entre los {len(SEL)} modelos del grupo {GRUPO}")
    guardar(fig, "A02_ciclo_anual")


if __name__ == "__main__":
    main()
