#!/usr/bin/env bash
# Orquestador del Entregable 3 (actividad c del TdR: proyecciones
# futuras de la TSM y del ENOS en Nino 3.4 y Nino 1+2 bajo SSP2-4.5,
# SSP3-7.0 y SSP5-8.5). Mismo criterio que rune2.sh: unico punto de entrada, pasos
# numerados, log propio. Solo calcula: las figuras van aparte.
#
# Uso: ./rune3.sh [STEP_FROM] [STEP_TO]
#   - Sin args: corre q01..q11 completos.
#   - Con args: rango de pasos (ej. ./rune3.sh q06 q11 rehace indices
#     -> eventos -> cambio de eventos -> espectro -> resumenes).
#   Pasos validos: q01 q02 q03 q04 q05 q06 q07 q08 q09 q10 q11
#
# Orden y dependencias entre pasos (ver data/processed/e3/README.md):
#   q01 series_cajas_1850-2100.nc             <- masked/ + seleccion de E2
#   q02 estado_medio_ref<ref>.csv,
#       serie_anual_anom_ref<ref>.csv         <- q01
#   q03 cambio_tsm_mapas_ref<ref>.nc          <- masked/ (campo 2D)
#   q04 ciclo_anual[_amplitud]_ref<ref>.csv   <- q01
#   q05 variabilidad_cajas_ref<ref>.csv,
#       variabilidad_estacional_ref<ref>.csv,
#       variabilidad_movil_30a.csv            <- q01
#   q06 indices_enso_<esc>_1850-2100.csv      <- q01
#   q07 eventos_<esc>_1850-2100.csv           <- q06 (incluye tipo costero/extendido/central)
#   q08 cambio_eventos_ref<ref>.csv           <- q06 + q07
#   q09 espectro_{indices,resumen}_ref<ref>.csv <- q06
#   q10 resumen_multimodelo_ref<ref>.csv      <- q02 + q04 + q05 + q08 + q09
#   q11 ens_*.csv, ens_mapas_ref<ref>.nc      <- q02 + q03 + q04 + q05 + q06 + q09
#       (mediana/p10/p90 por grupo 15/40/11/7: lo que leen las figuras)
# (<ref> = 1985-2014; periodos futuros P1 2036-2065 y P2 2071-2100, de
# config/periods.yaml.) q03 es independiente del resto; q02, q04, q05 y
# q06 solo dependen de q01; q10 y q11 van al final.
#
# Lee unicamente lo que dejaron E1 (data/processed/masked/) y E2
# (data/processed/e2/seleccion_1900-2014.csv, los 15 modelos
# seleccionados); no reprocesa nada de esos entregables.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p logs

# Argumentos leidos ANTES de activar conda: los scripts activate.d de
# algunos paquetes pueden pisar $1/$2 del script que los invoca.
STEP_FROM="${1:-q01}"
STEP_TO="${2:-q11}"

# Entorno conda: mismo bloque que run.sh (ver ahí el porqué de cada
# parte) -- en una máquina nueva alcanza con haber hecho una vez
# "conda env create -f environment.yml".
set +eu
if command -v conda >/dev/null 2>&1 && [ "$(basename "${CONDA_PREFIX:-}")" != "smn_toe" ]; then
    eval "$(conda shell.bash hook 2>/dev/null)" || true
    if conda env list 2>/dev/null | grep -qE '(^|[[:space:]])smn_toe([[:space:]]|$)'; then
        conda activate smn_toe 2>/dev/null || true
    elif conda env list 2>/dev/null | grep -qE '(^|[[:space:]])e1_smn([[:space:]]|$)'; then
        conda activate e1_smn 2>/dev/null || true
    fi
fi
set -eu
if [ -n "${CONDA_PREFIX:-}" ]; then
    export PATH="$CONDA_PREFIX/bin:$PATH"
fi
export PYTHONNOUSERSITE=1

MASKED_DIR="data/processed/masked"
SELECCION_E2="data/processed/e2/seleccion_1900-2014.csv"
OUT_DIR="data/processed/e3"
LOG_FILE="logs/pipeline_e3.log"

if ! ls "$MASKED_DIR"/tos_*_ssp245.nc >/dev/null 2>&1; then
    echo "Faltan datos de E1 en $MASKED_DIR -- corre ./run.sh (Entregable 1) primero." >&2
    exit 1
fi
if [ ! -f "$SELECCION_E2" ]; then
    echo "Falta $SELECCION_E2 -- corre ./rune2.sh (Entregable 2) primero." >&2
    exit 1
fi
if ! python3 -c "import numpy, pandas, xarray, netCDF4, scipy, yaml" 2>/dev/null; then
    echo "Al entorno de Python ($(command -v python3)) le faltan dependencias de E3." >&2
    echo "Actualizalo con: conda env update -n smn_toe -f environment.yml" >&2
    exit 1
fi

STEP_ORDER=(q01 q02 q03 q04 q05 q06 q07 q08 q09 q10 q11)

index_of () {
    local target="$1"
    for i in "${!STEP_ORDER[@]}"; do
        if [ "${STEP_ORDER[$i]}" = "$target" ]; then
            echo "$i"
            return
        fi
    done
    echo "-1"
}

FROM_IDX=$(index_of "$STEP_FROM")
TO_IDX=$(index_of "$STEP_TO")
if [ "$FROM_IDX" -lt 0 ] || [ "$TO_IDX" -lt 0 ]; then
    echo "Paso desconocido (recibido: desde='$STEP_FROM' hasta='$STEP_TO'). Pasos validos: ${STEP_ORDER[*]}" >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
echo "== rune3.sh: $(date '+%Y-%m-%d %H:%M:%S') (pasos $STEP_FROM..$STEP_TO) ==" | tee -a "$LOG_FILE"

# Corre "$@" si el paso está dentro del rango. Un paso que falla corta
# la corrida (set -e + pipefail): los siguientes dependen de él.
run_step () {
    local name="$1"; shift
    local idx; idx=$(index_of "$name")
    if [ "$idx" -ge "$FROM_IDX" ] && [ "$idx" -le "$TO_IDX" ]; then
        echo "== Paso $name: $* ==" | tee -a "$LOG_FILE"
        local t0; t0=$(date +%s)
        "$@" 2>&1 | tee -a "$LOG_FILE"
        echo "   ($name: $(( $(date +%s) - t0 )) s)" | tee -a "$LOG_FILE"
    fi
}

run_step q01 python3 scripts_e3/q01_series_cajas.py
run_step q02 python3 scripts_e3/q02_estado_medio.py
run_step q03 python3 scripts_e3/q03_mapas_cambio.py
run_step q04 python3 scripts_e3/q04_ciclo_anual.py
run_step q05 python3 scripts_e3/q05_variabilidad.py
run_step q06 python3 scripts_e3/q06_indices_futuros.py
run_step q07 python3 scripts_e3/q07_eventos_futuros.py
run_step q08 python3 scripts_e3/q08_cambio_eventos.py
run_step q09 python3 scripts_e3/q09_espectro.py
run_step q10 python3 scripts_e3/q10_resumen_multimodelo.py
run_step q11 python3 scripts_e3/q11_ensamble.py

echo "== rune3.sh terminado: $(date '+%Y-%m-%d %H:%M:%S') -- salidas en $OUT_DIR/ ==" | tee -a "$LOG_FILE"
ls -1 "$OUT_DIR" | tee -a "$LOG_FILE"
