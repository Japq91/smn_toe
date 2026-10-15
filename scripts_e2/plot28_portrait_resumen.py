#!/usr/bin/env python3
"""plot28 -- figura e2_10_portrait_resumen.png (seccion 10 y 10b de scripts_e2/plots_e2.ipynb).

Resumen cruzado (portrait diagram) y tabla de errores absolutos por modelo.

Entrada: salidas de p01-p09 (sesgo, climatologia, variabilidad, indices, eventos, Taylor compuesto, skill score)
Salida: figures/e2/e2_10_portrait_resumen.png
y figures/e2/e2_10_resumen_metricas.csv (tabla 10b)

Uso: python3 scripts_e2/plot28_portrait_resumen.py   (o bash rune2plot.sh 28 28)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot00_comun import *  # noqa: F401,F403  (config, helpers y cargas comunes)


def main():
    sesgo_caja, var_caja = cargar_sesgo_caja(), cargar_var_caja()
    clim, clim_obs = cargar_clim()
    est, ev, siglos = cargar_est(), cargar_eventos(), cargar_siglos()
    tcv, skv, o = cargar_tcv(), cargar_skv(), orden_s_final()
    sel = skv[VENTANA]["seleccionado"]

    frec = {}
    for i in INDICES:
        n_ev = ev[i]["number"].value_counts().reindex(datasets, fill_value=0)
        f = n_ev / pd.Series({n: siglos[(n, i)] for n in datasets})
        frec[i] = np.abs(np.log2(f[numbers] / f["OBS"]))

    err = pd.DataFrame({
        "|sesgo| Niño3.4": sesgo_caja["Niño3.4"].abs(),
        "|sesgo| Niño1+2": sesgo_caja["Niño1+2"].abs(),
        "|sesgo| ciclo anual N3.4": (clim["nino34"] - clim_obs["nino34"]).abs().mean(axis=1),
        "|Δσ| Niño3.4": var_caja["Niño3.4"].abs(),
        "|Δσ| Niño1+2": var_caja["Niño1+2"].abs(),
        "|Δskew| ICEN": (est.loc[numbers, "skew_ICEN"] - est.loc["OBS", "skew_ICEN"]).abs(),
        "frec. eventos ONI": frec["ONI"],
        "frec. eventos ICEN": frec["ICEN"],
        **{f"1-r compuesto {i} ±{v}m": 1 - tcv[v][i].drop(index="OBS")["r"] for i in ["ONI", "ICEN"] for v in VENTANAS},
        **{f"1-S_final ±{v}m": 1 - skv[v]["S_final"] for v in VENTANAS},
    }).reindex(o.index)
    rel = (err - err.median()) / err.median()

    fig, ax = plt.subplots(figsize=(13, 11))
    im = ax.imshow(rel.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(rel.shape[1]))
    ax.set_xticklabels(rel.columns, rotation=45, ha="right")
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=45, ha="left")
    ax.set_yticks(range(len(rel)))
    ax.set_yticklabels([f"{k+1:2d}. {etiqueta[n]}" + (" ✓" if sel[n] else "") for k, n in enumerate(rel.index)], fontsize=7)
    for lab, n in zip(ax.get_yticklabels(), rel.index):
        lab.set_fontweight("bold" if sel[n] else "normal")
    ax.axvline(rel.shape[1] - len(VENTANAS) - 0.5, color="k", lw=1.5)
    fig.colorbar(im, ax=ax, shrink=0.4, label="error relativo a la mediana multimodelo", extend="both")
    ax.set_title(f"Portrait diagram -- modelos ordenados por S_final ±{VENTANA} m", pad=110)
    plt.tight_layout()
    guardar(fig, "10_portrait_resumen")

    # 10b. Tabla de errores absolutos
    resumen = err.copy()
    for v in reversed(VENTANAS):
        resumen.insert(0, f"rank ±{v}m", skv[v]["S_final"].rank(ascending=False, method="min").astype(int))
        resumen.insert(1, f"S_final ±{v}m", skv[v]["S_final"])
    resumen.insert(0, "seleccionado", sel.reindex(resumen.index))
    resumen.insert(0, "modelo", resumen.index.map(nombre))
    out_csv = OUT_FIG / "e2_10_resumen_metricas.csv"
    resumen.to_csv(out_csv, float_format="%.4f")
    print(f"Listo: {out_csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
