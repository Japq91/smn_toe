#!/usr/bin/env bash
# Orquestador del Entregable 2 (climatología, sesgos, ONI/RONI/ICEN,
# diagrama de Taylor, eventos, skill score). Mismo criterio que run.sh
# (E1): único punto de entrada, pasos numerados, log propio.
#
# Uso: ./rune2.sh [STEP_FROM] [STEP_TO]
#   - Sin args: corre p01..p09 completos.
#   - Con args: rango de pasos (ej. ./rune2.sh p07 p09 rehace solo
#     eventos -> Taylor compuesto -> skill score).
#   Pasos válidos: p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11
#
# Orden y dependencias entre pasos (ver data/processed/e2/README.md):
#   p01 indices_enso_<y0>-<y1>.csv          <- masked/ + model_registry_e2.csv
#   p02 climatologia_<caja>_<ref>.csv       <- masked/
#   p03 sesgo_tsm_ref<ref>.nc               <- masked/
#   p04 variabilidad_tsm_ref<ref>.nc        <- masked/
#   p05 taylor_<caja>_ref<ref>.csv          <- masked/
#   p06 correlacion_tsm_ref<ref>.nc         <- masked/
#   p07 eventos_<INDICE>_<y0>-<y1>.csv      <- p01  (<y0>-<y1> = periodo de indices_enso)
#   p08 taylor_compuesto_<INDICE>_vent<N>m  <- p01 + p07  (N = 12, 15, 18)
#   p09 skill_score_vent<N>m_<y0>-<y1>.csv  <- p05 + p08  (N = 12, 15, 18)
#   p10 pruebas_eventos_<y0>-<y1>.csv       <- p01 + p07  (filtro de eventos RONI/ICEN)
#   p11 seleccion_<y0>-<y1>.csv             <- p09 + p10  (seleccion final)
# p02-p06 son independientes entre sí; p07-p09 son una cadena y deben
# correr en ese orden después de p01/p05. Todo lo que generan es lo que
# leen después los gráficos de E2 (rune2plot.sh -> figures/e2/).
#
# Este script NO descarga ni reprocesa nada de CMIP6/ERSSTv5 -- lee
# únicamente lo que el Entregable 1 ya dejó en data/processed/masked/
# (ver scripts_e2/README.md para el contrato de entrada exacto).
# Si esos archivos no existen todavía, corré primero ./run.sh (E1).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p logs

# Argumentos leidos ANTES de activar conda: los scripts activate.d de
# algunos paquetes pueden pisar $1/$2 del script que los invoca.
STEP_FROM="${1:-p01}"
STEP_TO="${2:-p11}"

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

# Entrada de solo lectura (producida por E1 / versionada en el repo)
MASKED_DIR="data/processed/masked"
OBS_FILE="$MASKED_DIR/ersstv5_region.nc"
REGISTRY_E2="data/processed/e2/model_registry_e2.csv"

# Salida propia de E2 (ver scripts_e2/README.md)
OUT_DIR="data/processed/e2"
FIGURES_DIR="figures/e2"
LOG_FILE="logs/pipeline_e2.log"

# Ventanas del compuesto (meses a cada lado del pico): 12 es el
# resultado principal, 15 y 18 son pruebas de sensibilidad.
VENTANAS=(12 15 18)

if [ ! -f "$OBS_FILE" ] || ! ls "$MASKED_DIR"/tos_*_historical.nc >/dev/null 2>&1; then
    echo "Faltan datos de E1 en $MASKED_DIR -- corré ./run.sh (Entregable 1) primero." >&2
    exit 1
fi
if [ ! -f "$REGISTRY_E2" ]; then
    echo "Falta $REGISTRY_E2 (versionado en git) -- restauralo con: git checkout -- $REGISTRY_E2" >&2
    exit 1
fi

# Dependencias de Python (environment.yml): se verifican antes de
# correr nada, para no descubrir a mitad de camino (ej. en p09) que el
# entorno quedó desactualizado.
if ! python3 -c "import numpy, pandas, xarray, netCDF4, scipy, sklearn" 2>/dev/null; then
    echo "Al entorno de Python ($(command -v python3)) le faltan dependencias de E2." >&2
    python3 -c "import numpy, pandas, xarray, netCDF4, scipy, sklearn" 2>&1 | tail -1 >&2 || true
    echo "Actualizalo con: conda env update -n smn_toe -f environment.yml" >&2
    exit 1
fi

STEP_ORDER=(p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11)

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

mkdir -p "$OUT_DIR" "$FIGURES_DIR"
echo "== rune2.sh: $(date '+%Y-%m-%d %H:%M:%S') (pasos $STEP_FROM..$STEP_TO) ==" | tee -a "$LOG_FILE"

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

run_step p01 python3 scripts_e2/p01_indices_enso.py
run_step p02 python3 scripts_e2/p02_climatologia.py
run_step p03 python3 scripts_e2/p03_sesgo.py
run_step p04 python3 scripts_e2/p04_variabilidad.py
run_step p05 python3 scripts_e2/p05_taylor.py
run_step p06 python3 scripts_e2/p06_correlacion.py
run_step p07 python3 scripts_e2/p07_eventos.py
for v in "${VENTANAS[@]}"; do
    run_step p08 python3 scripts_e2/p08_taylor_compuesto.py "$v"
done
for v in "${VENTANAS[@]}"; do
    run_step p09 python3 scripts_e2/p09_skill_score.py "$v"
done
run_step p10 python3 scripts_e2/p10_pruebas_eventos.py
run_step p11 python3 scripts_e2/p11_seleccion.py

echo "== rune2.sh terminado: $(date '+%Y-%m-%d %H:%M:%S') -- salidas en $OUT_DIR/ ==" | tee -a "$LOG_FILE"
ls -1 "$OUT_DIR" | tee -a "$LOG_FILE"
