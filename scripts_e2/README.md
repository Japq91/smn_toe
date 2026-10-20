 # scripts_e2/

Código del Entregable 2: climatología, sesgo, ONI/RONI (Niño 3.4) e
ICEN (Niño 1+2), diagrama de Taylor -- ver
`e2_informe/informe_e2.tex` (Sección 3, Marco metodológico) para las
ecuaciones/citas y la Sección 2 (Alcance) del mismo informe para lo
que exige el TdR. No se usan Índices C/E (Takahashi et al.,
2011): decisión del usuario, reemplazados por ONI/RONI/ICEN.

**Sin corrección Linear Scaling (LS)**: se probó y se descartó -- LS es
una resta constante por mes calendario, y cualquier anomalía (que es
todo lo que se calcula acá: ONI, RONI, ICEN, variabilidad, correlación,
Taylor) la cancela algebraicamente sola. Los índices se calculan
directamente como anomalía respecto a la climatología **propia** de
cada dataset (ERSSTv5 con la suya, cada modelo con la suya) -- mismo
criterio con el que se calcula ONI en la práctica real, sin mezclar
climatologías entre fuentes. El sesgo (`C_m^modelo - C_m^obs`) se sigue
reportando como diagnóstico independiente (lo pide el TdR), pero ya no
alimenta ningún cálculo posterior.

Contrato de entrada, fijo y de solo lectura, producido por el
Entregable 1 (`scripts/`, `run.sh`):

- `data/processed/models_inventory_final.csv` -- filtrar por
  `selected == "True"` para saber qué modelos usar (los mismos 40 que
  documenta el informe de E1).
- `data/processed/masked/tos_<modelo>_<experimento>.nc` -- SST ya
  homogeneizada (grilla, calendario, unidades, máscara océano-tierra
  compartidas con ERSSTv5).
- `data/processed/masked/ersstv5_region.nc` -- referencia
  observacional.

Salidas propias del Entregable 2, todas anidadas bajo el mismo
directorio raíz por tipo de contenido que usa E1 (en vez de carpetas
sueltas `data_e2/`/`figuras_e2/` en la raíz del repo -- E3 y E4 del
mismo TdR van a necesitar el mismo patrón):

- `data/processed/e2/` -- datos procesados propios de E2.
- `figures/e2/` -- figuras generadas por estos scripts.
- `e2_informe/figuras/` -- symlinks curados hacia `figures/e2/` para
  `e2_informe/informe_e2.tex` (mismo criterio que
  `e1_informe/figuras/` para E1, ver su README).

Ningún script de esta carpeta debe escribir fuera de esos tres
subdirectorios, ni modificar nada bajo `scripts/`, `run.sh` o
`data/processed/masked/` -- eso es responsabilidad exclusiva del
pipeline de E1.

## Scripts

`p01`...`p11` -- ver `data/processed/e2/README.md` para el listado
completo con el punto del cálculo que cubre cada uno y el detalle de
su archivo de salida. `p09_skill_score.py` calcula el score de habilidad (Taylor, 2001)
a partir de `p05_taylor.py` y `p08_taylor_compuesto.py`;
`p10_pruebas_eventos.py` hace el filtro estadístico de eventos y
`p11_seleccion.py` cierra la cadena con la selección final (filtro +
`S_final` ≥ 0.9 + `S_ICEN` ≥ 0.9). Se corren con `./rune2.sh [desde] [hasta]`.

`plot<codigo>_<nombre>.py` -- un script por figura, que genera
`figures/e2/e2_<codigo>_<nombre>.png` a partir de lo que dejó
`rune2.sh`. Se corren con `bash rune2plot.sh [desde] [hasta]` (por
código de figura: `07` corre 07a..07e, `07c` solo esa). Comparten
configuración, cargas y funciones de dibujo (mapas, barras de color,
diagrama de Taylor) en `plot00_comun.py`. Salieron de
`plots_e2.ipynb`, que es un prototipo local no versionado: los
scripts son la versión vigente.

## Convenciones de datos de E2

Documentadas en `data/processed/e2/README.md` (numeración de modelos
`M01..M40`, formato del CSV de índices, y el recorte a la ventana
temporal común a los 40 modelos por la disponibilidad de IITM-ESM) --
no se duplican acá.
