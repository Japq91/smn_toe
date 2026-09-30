"""Figura de reemplazo de cmip6_contribution.png: modelos seleccionados
por pais de la institucion (desde informe/model_registry.csv y el
inventario final). Reproducible, a diferencia del mapa externo."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = "/home/jonathan/personal/e1_smn"
OUT = f"{REPO}/revision_e1/figuras/contribucion_paises.png"
ES = {"USA": "Estados Unidos", "China": "China", "France": "Francia",
      "Germany": "Alemania", "Canada": "Canadá", "Sweden": "Suecia",
      "Japan": "Japón", "Australia": "Australia", "Italy": "Italia",
      "Russia": "Rusia", "Norway": "Noruega", "India": "India",
      "Republic of Korea": "Corea del Sur", "Taiwan": "Taiwán",
      "UK": "Reino Unido"}
INK, INK2, SERIE = "#0b0b0b", "#52514e", "#2a78d6"

reg = pd.read_csv(f"{REPO}/informe/model_registry.csv")
sel = set(pd.read_csv(f"{REPO}/data/processed/models_inventory_final.csv").model)
s = reg[reg.model.isin(sel)].copy()
s["pais"] = s.country.map(ES).fillna(s.country)
g = (s.groupby("pais")
       .agg(modelos=("model", "size"), inst=("institution", "nunique"),
            lista=("institution", lambda x: ", ".join(sorted(set(x)))))
       .sort_values(["modelos", "pais"], ascending=[True, False]))

fig, ax = plt.subplots(figsize=(8.2, 5.4), dpi=200)
y = range(len(g))
ax.barh(list(y), g.modelos, color=SERIE, height=0.62, edgecolor="white", linewidth=1)
for yi, (n, lista) in zip(y, zip(g.modelos, g.lista)):
    ax.text(n + 0.12, yi, f"{n}   {lista}", va="center", fontsize=7.6, color=INK2)
ax.set_yticks(list(y), g.index, fontsize=9, color=INK)
ax.set_xlim(0, g.modelos.max() + 5.2)
ax.set_xticks(range(0, int(g.modelos.max()) + 1))
ax.tick_params(axis="x", colors=INK2, labelsize=8)
ax.set_xlabel("Número de modelos seleccionados", fontsize=9, color=INK2)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#b9b8b3")
ax.grid(axis="x", color="#e6e5e0", linewidth=0.6)
ax.set_axisbelow(True)
ax.tick_params(axis="y", length=0)
ax.set_title(f"{len(s)} modelos seleccionados · {s.institution.nunique()} instituciones · "
             f"{s.pais.nunique()} países", fontsize=10, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT, facecolor="white")
print(OUT)
print(g[["modelos", "inst"]].to_string())
