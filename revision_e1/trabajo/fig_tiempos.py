"""Figura del anexo: duracion de cada paso de run.sh medida en esta
maquina (logs/step_timings.csv). Se usa el maximo registrado por paso,
que corresponde a una corrida que hizo todo el trabajo (primera vez)."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = "/home/jonathan/personal/e1_smn"
OUT = f"{REPO}/revision_e1/figuras/anexo_tiempos.png"
INK, INK2, SERIE = "#0b0b0b", "#52514e", "#2a78d6"
NOMBRES = {"00b": "00b  Lista de modelos (ESGF)", "01": "01  Catálogo de archivos",
           "02": "02  Descarga CMIP6", "04": "04  Regrillado",
           "05": "05  Máscara", "06": "06  Control de calidad", "07": "07  Inventario"}

t = pd.read_csv(f"{REPO}/logs/step_timings.csv")
t = t[t.step.astype(str).isin(NOMBRES)]
mx = t.groupby(t.step.astype(str)).seconds.max().reindex(list(NOMBRES)).fillna(0) / 3600.0


def etiqueta(h):
    m = h * 60
    if m < 1:
        return "< 1 min"
    if m < 90:
        return f"{m:.0f} min"
    return f"{h:.1f} h".replace(".", ",")


fig, ax = plt.subplots(figsize=(8.2, 3.6), dpi=200)
y = list(range(len(mx)))[::-1]
ax.barh(y, mx.values, color=SERIE, height=0.6)
for yi, h in zip(y, mx.values):
    ax.text(h + 0.15, yi, etiqueta(h), va="center", fontsize=8.5, color=INK2)
ax.set_yticks(y, [NOMBRES[s] for s in mx.index], fontsize=9, color=INK)
ax.set_xlabel("Horas (máximo registrado en esta máquina)", fontsize=9, color=INK2)
ax.set_xlim(0, mx.max() * 1.15)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#b9b8b3")
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=INK2, labelsize=8)
ax.grid(axis="x", color="#e6e5e0", linewidth=0.6)
ax.set_axisbelow(True)
ax.set_title("Duración de cada paso en una corrida completa desde cero", fontsize=10,
             color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT, facecolor="white")
print(OUT)
print(mx.round(2).to_string())
