# data/processed/e3/

Salidas del Entregable 3 (proyecciones futuras), generadas por
`scripts_e3/qXX_*.py` (`./rune3.sh`). Solo se versiona este README; el
resto se regenera en cada máquina. Decisiones de método en
`scripts_e3/README.md`.

Convenciones comunes a todos los archivos:

- `number` = M01..M40 (`data/processed/e2/model_registry_e2.csv`),
  `modelo` = nombre CMIP6, `seleccionado` = uno de los 15 modelos de E2.
- `escenario` ∈ {ssp245, ssp370, ssp585}.
- `periodo` ∈ {ref, P1, P2}, con `anios` = 1985-2014, 2036-2065 y
  2071-2100.
- `caja` ∈ {nino34, nino12, tropical}. tropical es 20S-20N, todas las
  longitudes, ponderada por cos(lat); se incluye como contraste.
- Los cambios (`delta*`) son siempre P − ref del mismo modelo.

## `series_cajas_1850-2100.nc` (q01)

`tos(number, escenario, caja, time)` [°C], mensual 1850-01 a 2100-12:
historical hasta 2014-12 y el escenario desde 2015-01. El tramo
histórico se repite en ambos escenarios. NaN donde el modelo no tiene
dato: IITM-ESM antes de 1900, y CAMS-CSM1-0 e IITM-ESM en 2100.
Coordenadas auxiliares `model` y `seleccionado`.

## `estado_medio_ref1985-2014.csv` (q02)

Una fila por (modelo, escenario, caja, periodo futuro): `tsm_ref`,
`tsm_fut`, `delta` [°C] y `delta_relativo` = delta_caja − delta_tropical.
`delta_relativo` > 0 indica que la caja se calienta más que el promedio
tropical (patrón "tipo El Niño").

## `serie_anual_anom_ref1985-2014.csv` (q02)

Media anual menos la media de la referencia, por (modelo, escenario,
caja, `year`), 1850–2100: `anom` y `anom_relativa` (caja menos
tropical). Sirve para las trayectorias y la pluma multimodelo.

## `cambio_tsm_mapas_ref1985-2014.nc` (q03)

Por (number, escenario, periodo ∈ {P1, P2}, lat, lon), en el dominio
completo de `masked/` (30S–30N, global):

- `delta_media` [°C]: cambio de la TSM media.
- `delta_relativo` [°C]: `delta_media` menos su promedio tropical
  20S–20N, es decir, el patrón del calentamiento.
- `delta_std_pct` [%]: cambio de σ de la anomalía sin tendencia.

Además trae `sigma_ref(number, lat, lon)`.

## `ciclo_anual_ref1985-2014.csv` y `ciclo_anual_amplitud_ref1985-2014.csv` (q04)

- `ciclo_anual_*`: una fila por (modelo, escenario, caja, periodo,
  `mes`), con `tsm` (climatología del mes) y `delta` (respecto de ref).
- `ciclo_anual_amplitud_*`: una fila por (modelo, escenario, caja,
  periodo), con `amplitud` (máx − mín), `delta_amplitud`, `mes_max` y
  `mes_min`.

## `variabilidad_cajas_ref1985-2014.csv` y `variabilidad_movil_30a.csv` (q05)

Las métricas salen de la anomalía sin climatología ni tendencia lineal
de cada ventana:

- `sigma`: anomalía mensual.
- `sigma_3m`: media móvil de 3 meses, en la escala del ONI/ICEN.
- `asimetria` (skewness).
- `curtosis` (exceso).
- Solo en el archivo por periodo: `delta_sigma_pct` y
  `delta_sigma_3m_pct` [%] respecto de ref.

`variabilidad_estacional_ref1985-2014.csv`: una fila por (modelo,
escenario, caja, periodo, `mes`), con `sigma_3m` de la estación de 3
meses centrada en el mes y `delta_sigma_3m_pct`. Muestra en qué época
del año se concentra la variabilidad.

El archivo móvil usa ventanas de 30 años con paso de 1 año e indica la
ventana con `anio_central`; trae `sigma`, `sigma_3m` y `asimetria`.

## `indices_enso_<escenario>_1850-2100.csv` (q06)

Mismo formato que `indices_enso_1900-2014.csv` de E2: índice `time` y
columnas `Mxx_ONI`, `Mxx_RONI`, `Mxx_ICEN`, `Mxx_ONIfija` y
`Mxx_ICENfija` (200 columnas). Definiciones:

- ONI y RONI: como en E2.
- ICEN: quinquenios del ENFEN sin el tope de base 1991–2020.
- RONI: escala de varianza fijada en 1985–2014.
- ONIfija e ICENfija: anomalía respecto de 1985–2014, sin quitar el
  calentamiento.

Diferencias con E2 en el tramo histórico:

- ONI e ICEN coinciden hasta ~1985. Después difieren porque las bases
  móviles ya no se truncan en 2014.
- El RONI difiere por un factor de escala constante.

## `eventos_<escenario>_1850-2100.csv` (q07)

Una fila por evento, con las columnas `indice`, `number`, `inicio`,
`fin`, `fecha_pico`, `duracion_meses`, `magnitud_pico`,
`categoria_oficial`, `categoria_relativa`, `periodo` y `tipo`.

- Umbrales de `scripts_e2/p07_eventos.py`.
- `categoria_relativa` usa la σ del índice en 1985–2014.
- `periodo` es el del pico; queda vacío si el pico cae fuera de ref, P1
  y P2.
- `tipo`, solo para ONI e ICEN: costero (evento ICEN sin evento ONI
  superpuesto), extendido (ambos se superponen) o central (evento ONI
  sin ICEN).

## `cambio_eventos_ref1985-2014.csv` (q08)

Una fila por (escenario, indice, modelo, periodo). Métricas:

- `n_eventos`, `siglos` (meses del periodo con TSM en la caja / 1200; 0.3
  con 30 años completos) y `frec_siglo` (eventos por siglo). Se cuentan
  los meses con TSM y no los meses con índice: la media móvil centrada de
  3 meses deja sin valor 2100-12 sin que falte ningún dato.
- `dur_media` [meses], `mag_media` y `mag_max`.
- `n_moderado_mas`, `n_fuerte_mas` y `n_extremo_rel`.
- `frac_meses_umbral`: fracción de meses sobre el umbral de inicio, sin
  exigir duración.
- `n_costero`, `n_extendido`, `n_central` y `frac_costero` (fracción
  de eventos ICEN que son costeros): solo ONI e ICEN.
- Solo en P1/P2: `razon_frec` = frec(P) / frec(ref).

Solo para ONI, RONI e ICEN en P1/P2, las pruebas frente a ref:

- `G_frec`/`p_frec`: razón de verosimilitud de Poisson.
- `A2_dur`/`p_dur`: Anderson-Darling de la duración.
- `G_est`/`p_est`: prueba G del mes del pico.
- `pholm_*`: valores p ajustados por Holm sobre las tres pruebas.
- `cambios`: las pruebas con p_holm < 0.05.

Las de duración y estacionalidad quedan en NaN si hay menos de 2 eventos
en alguno de los dos periodos.

## `espectro_indices_ref1985-2014.csv` y `espectro_resumen_ref1985-2014.csv` (q09)

Espectro de Welch de ONI, RONI e ICEN en cada periodo (`fs=12`,
ventana de Hann, `nperseg=180`, 50 % de solapamiento: 3 segmentos de 15
años por periodo):

- `espectro_indices_*`: una fila por (escenario, indice, modelo,
  periodo, `frecuencia` [ciclos/año]), con `periodo_anios` y `potencia`.
- `espectro_resumen_*`: una fila por (escenario, indice, modelo,
  periodo), con `periodo_pico_anios` (máximo de potencia en 1.5–10 años)
  y `frac_banda_enso` (fracción de la varianza en 2–7 años).

## `espectro_indices_86a.csv` y `espectro_resumen_86a.csv` (q09)

Mismo espectro en dos tramos del mismo largo, 86 años (1032 meses):
histórico 1929–2014 frente a cada escenario 2015–2100 (`nperseg=256`,
como E2: 7 segmentos de 21.3 años). Es lo que dibuja la Figura A9.

- `fuente`: archivo de índices usado (`indices_enso_<fuente>_1850-2100.csv`);
  el tramo histórico se calcula con los tres, porque la base móvil del
  índice cerca de 2014 depende levemente del escenario.
- `tramo`: `historical` (1929–2014) o el escenario (2015–2100).
- `espectro_indices_86a`: una fila por (fuente, tramo, indice, modelo,
  `frecuencia`), con `periodo_anios` y `potencia`.
- `espectro_resumen_86a`: una fila por (fuente, tramo, indice, modelo),
  con `anios`, `n_meses`, `periodo_pico_anios` y `frac_banda_enso`.

## `resumen_multimodelo_ref1985-2014.csv` (q10)

Una fila por (`grupo` ∈ {15, 40, 11, 7}, escenario, periodo, `variable`,
`caja_indice`). Grupos:

- 15: selección de E2.
- 40: todos.
- 11: los 15 sin M34, M35, M12 y M40.
- 7: criterio anterior S ≥ 0.9.

Columnas: `n_modelos`, `media`, `mediana`, `p10`, `p90`, `minimo`,
`maximo`, `p_wilcoxon`, `pholm_wilcoxon` y `signif`.

- `p_wilcoxon`: prueba de rangos con signo sobre los modelos del grupo.
  En las variables de cambio, contra el valor neutro; en las de nivel,
  P frente a ref, pareando cada modelo consigo mismo. No se calcula para
  `amplitud`, cuya prueba sería la misma que la de `delta_amplitud`.
- `pholm_wilcoxon`: ajustado por Holm dentro de cada tabla (grupo,
  escenario, periodo), unas 69 pruebas.
- `signif`: `pholm_wilcoxon` < 0.05. En los grupos 7 y 11 es siempre
  falso: el p mínimo de Wilcoxon (2/2^n) multiplicado por ~69 supera
  0.05. Esos grupos se leen por mediana y acuerdo de signo.

En las variables de cambio (`delta*`, `razon_frec`, solo P1/P2) se
agregan:

- `n_aumentan`: modelos con cambio > 0, o razón > 1.
- `acuerdo_signo`: fracción de modelos que coinciden con el signo de la
  mediana; ≥ 0.8 es robusto según el criterio simple del IPCC AR6. NaN
  si la mediana es igual al valor neutro.

Las variables de nivel (`amplitud`, `sigma_3m`, `asimetria`,
`curtosis`, `frec_siglo`, `frac_costero`, `periodo_pico_anios`, …) se
resumen también en ref.

## `ens_*` (q11): productos multimodelo para las figuras

Estadísticos por grupo (15, 40, 11, 7). Los CSV traen las columnas
clave, `variable`, `n_modelos`, `mediana`, `p10` y `p90`.

| Archivo | Claves | Variables |
|---|---|---|
| `ens_serie_anual_ref1985-2014.csv` | escenario, caja, year | anom, anom_relativa |
| `ens_ciclo_anual_ref1985-2014.csv` | escenario, caja, periodo, mes | tsm, delta |
| `ens_variabilidad_movil_30a.csv` | escenario, caja, anio_central | sigma_3m, delta_sigma_3m_pct (respecto de la ventana centrada en 2000) |
| `ens_variabilidad_estacional_ref1985-2014.csv` | escenario, caja, periodo, mes | sigma_3m, delta_sigma_3m_pct |
| `ens_espectro_ref1985-2014.csv` | escenario, indice, periodo, frecuencia | potencia |
| `ens_espectro_86a.csv` | fuente, tramo, indice, frecuencia | potencia |
| `ens_indices_1850-2100.csv` | escenario, indice, time | valor |

`ens_mapas_ref1985-2014.nc` tiene dimensiones (grupo, escenario,
periodo, lat, lon). Para cada campo (`delta_media`, `delta_relativo` y
`delta_std_pct`) trae tres variables:

- `<var>_media`;
- `<var>_mediana`;
- `<var>_acuerdo`: fracción de modelos con el signo de la mediana.
