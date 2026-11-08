# scripts_e3/

Código del Entregable 3 (actividad c) del TdR): proyecciones futuras de
la TSM y de la variabilidad del ENOS en Niño 3.4 y Niño 1+2 bajo
SSP2-4.5, SSP3-7.0 y SSP5-8.5, evaluando el cambio del estado medio, del ciclo
anual, de la variabilidad y de la ocurrencia de eventos cálidos (ONI,
RONI, ICEN). El cálculo está en `qXX_*.py` (`./rune3.sh`). Las figuras
salen de un solo notebook, `plots_e3.ipynb`, que solo lee lo que dejan
q01–q11 y guarda en `figures/e3/`. Su sección 7 permite repetir a mano
las pruebas estadísticas y compararlas con las del pipeline. Los
estadísticos multimodelo ya vienen calculados en q10 y q11.

Contrato de entrada, de solo lectura:

- `data/processed/masked/tos_<modelo>_{historical,ssp245,ssp370,ssp585}.nc`
  (E1).
- `data/processed/e2/model_registry_e2.csv` -- numeración M01..M40.
- `data/processed/e2/seleccion_1900-2014.csv` (E2, p11) -- columna
  `seleccionado`: los 15 modelos que pasan el filtro de eventos.

Salida: solo `data/processed/e3/` (cálculo) y `figures/e3/` (notebook).

## Decisiones de método

Todas son constantes de `common_e3.py`, o del script que las usa, y
se pueden cambiar en un solo lugar:

- **Escenarios**: `ESCENARIOS = ["ssp245", "ssp370", "ssp585"]`. El
  notebook dibuja los de `ESCS` (por defecto, los tres).
- **Periodos**: referencia 1985–2014 frente a P1 2036–2065 y P2
  2071–2100 (los dos últimos, de `config/periods.yaml`). La referencia
  tiene 30 años, igual que P1 y P2, y no los 34 de 1981–2014: así las σ
  y los conteos de eventos se comparan sobre muestras del mismo largo.
  Es además la base fija del RONI en E2.
- **Cada modelo contra sí mismo**: todos los cambios son P − ref del
  mismo modelo, de modo que el sesgo medio diagnosticado en E2 se
  cancela.
- **Variabilidad**: anomalía de cada ventana de 30 años sin su
  climatología mensual ni su tendencia lineal
  (`common_e3.anomalia_sin_tendencia`). Sin quitar la tendencia, el
  calentamiento dentro de la ventana inflaría σ.
- **Índices hasta 2100**:
  - ONI con las bases móviles del CPC, como en E2. La última base es
    2071–2100.
  - ICEN con los quinquenios del ENFEN, pero **sin el tope de base
    1991–2020** de la Nota Técnica. Con el tope, todo el calentamiento
    futuro se leería como El Niño permanente.
  - RONI con base fija 1985–2014. El factor de escala de la varianza
    se calcula **en la base**, no en toda la serie, para que no absorba
    el cambio futuro de varianza.
  - **ONIfija/ICENfija**: anomalía respecto de 1985–2014, sin quitar el
    calentamiento. Responden "¿cuánto tiempo se superan los umbrales de
    hoy?", que mezcla el cambio de la media con el del ENOS.
- **Eventos**: umbrales y categorías de `scripts_e2/p07_eventos.py`
  (importados, no copiados). La categoría relativa (Shin et al. 2022)
  usa la σ del índice en la referencia y no la de toda la serie, para
  que "extremo" signifique lo mismo en todos los periodos.
- **Grupos de modelos** (`common_e3.grupos()`):
  - 15: la selección de E2, conjunto principal.
  - 40: contraste.
  - 11: los 15 sin los de ICEN débil (M34, M35, M12, M40).
  - 7: el criterio anterior, S_final y S_ICEN ≥ 0.9.

  Las dos últimas son las pruebas de sensibilidad que recomienda el
  informe de E2. q10 y q11 resumen todo para los cuatro.
- **Tipo de evento** (q07): se cruzan los eventos ICEN y ONI del mismo
  modelo. Son el mismo episodio si se superponen al menos un mes.
  Resultan tres tipos: costero (solo ICEN), extendido (ambos) y central
  (solo ONI).
- **Espectro** (q09): el método de la figura 04d de E2 (Welch, `fs=12`,
  Hann, sin tendencia lineal), aplicado a cada periodo de 30 años, pero
  con segmentos de 180 meses en vez de 256. Con 256 Welch usaría un solo
  segmento de los 360 meses del periodo; con 180 salen 3, que los cubren
  completos. La resolución (1/15 ciclos/año) alcanza para la banda del
  ENOS, pero no para separar periodos vecinos.
- **Significancia multimodelo** (q10): prueba de Wilcoxon sobre los
  modelos del grupo, con corrección de Holm dentro de cada tabla (grupo,
  escenario, periodo). Complementa al acuerdo de signo y a las pruebas
  por modelo de q08. Con 7 u 11 modelos ninguna prueba sobrevive a Holm,
  por lo que esos grupos se leen por mediana y acuerdo de signo.
- **Pruebas de cambio** (q08): las tres de `p10_pruebas_eventos.py`
  (Poisson, Anderson-Darling, G del mes del pico) con Holm. Se compara
  P contra la referencia del mismo modelo. Se usan 1999 permutaciones
  (9999 en E2). Con 6–12 eventos por periodo la potencia por modelo es
  baja; la conclusión sale del conjunto (q10).
- **Inicio de la serie en 1850**: p01 de E2 calcula las bases móviles
  sobre la serie desde 1850. Para que el tramo histórico coincida hay
  que partir del mismo año. IITM-ESM (M26) empieza en 1900, y
  CAMS-CSM1-0 e IITM-ESM terminan en 2099-12.

## Scripts

`q01`…`q11`: ver la tabla en `README.md` (raíz) y el detalle de cada
salida en `data/processed/e3/README.md`. Se corren con
`./rune3.sh [desde] [hasta]` o sueltos
(`python3 scripts_e3/qXX_*.py`).
