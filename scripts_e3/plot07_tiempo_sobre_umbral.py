#!/usr/bin/env python3
"""plot07 -- Figura 7 del informe E3: figures/e3/e3_07_tiempo_sobre_umbral.png

Fracción de meses con el índice sobre el umbral de inicio de El Niño, en P1 y P2,
para las bases móviles (ONI, RONI, ICEN) y fijas (ONIfija, ICENfija). Cajas =
distribución entre los modelos del grupo; número bajo cada caja: mediana.

Entrada: cambio_eventos_ref<ref>.csv (q08) (data/processed/e3/)
Salida: figures/e3/e3_07_tiempo_sobre_umbral.png

Uso: python3 scripts_e3/plot07_tiempo_sobre_umbral.py   (o bash rune3plot.sh 07)
     E3_GRUPO=40 python3 scripts_e3/plot07_tiempo_sobre_umbral.py   -> otro conjunto, con sufijo _g40
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun_e3 import *  # noqa: F401,F403  (config, cargas y funciones de dibujo comunes)


def main():
    ind_umbral = INDICES + ["ONIfija", "ICENfija"]
    ev_sel = cambio_ev()[cambio_ev().number.isin(SEL)]
    cats = [("historical", "ref")] + [(e, None) for e in ESCS]
    ancho = 0.8 / len(cats)
    desp = (np.arange(len(cats)) - (len(cats) - 1) / 2) * ancho
    fig, axs = plt.subplots(2, 1, figsize=(8, 6), layout="constrained", sharey=True)
    for j, per in enumerate(FUTS):
        ax = axs[j]
        for k, (esc, _) in enumerate(cats):
            e, p = ("ssp245", "ref") if esc == "historical" else (esc, per)
            datos = [ens(ev_sel, indice=ind, escenario=e, periodo=p)["frac_meses_umbral"].dropna().to_numpy()
                     for ind in ind_umbral]
            dibujar_cajas(ax, datos, np.arange(1, len(ind_umbral) + 1) + desp[k], esc, ancho,
                          [np.median(d) if len(d) else np.nan for d in datos], fmt="{:.2f}")
        separadores(ax, len(ind_umbral))
        ax.axvline(3.5, color="0.4", lw=0.8)       # bases moviles | base fija
        ax.set_xticks(range(1, len(ind_umbral) + 1), ind_umbral)
        ax.set_ylim(-0.2, 1.05)
        ax.set_yticks(np.arange(0, 1.01, 0.2))
        ax.set_ylabel("meses sobre el umbral\nfracción")
        p0.titulo_panel(ax, LETRAS[j], NOM_PER[per])
    leyenda_cajas(fig, [(e, None) for e, _ in cats], extra="número bajo cada caja: mediana")
    fig.suptitle(f"Tiempo sobre el umbral de inicio\ndistribución entre los {len(SEL)} modelos del grupo {GRUPO}")
    guardar(fig, "07_tiempo_sobre_umbral")


if __name__ == "__main__":
    main()
