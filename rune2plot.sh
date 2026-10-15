#!/usr/bin/env bash
# Figuras del Entregable 2: corre solo los scripts de graficos
# scripts_e2/plotNN_*.py (salidos de scripts_e2/plots_e2.ipynb), en orden,
# sobre lo que rune2.sh ya dejo en data/processed/e2/.
#
# Uso: bash rune2plot.sh [DESDE] [HASTA]
#   - Sin args: plot01..plot28 (todas las figuras).
#   - Con args: rango por numero (ej. bash rune2plot.sh 17 21 rehace
#     solo las figuras de eventos; bash rune2plot.sh 28 28 solo el portrait).
#
# Salida: figures/e2/e2_<seccion>_<nombre>.png (mismo nombre que el
# notebook) + figures/e2/e2_10_resumen_metricas.csv (plot28). Log en
# logs/plots_e2.log. Una figura que falla no corta las demas (no
# dependen entre si); al final se listan las que fallaron y el script
# sale con error si hubo alguna.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p logs

# Argumentos leidos ANTES de activar conda: los scripts activate.d de
# algunos paquetes pueden pisar $1/$2 del script que los invoca.
DESDE="${1:-01}"
HASTA="${2:-99}"

# Entorno conda: mismo bloque que run.sh / rune2.sh.
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

LOG_FILE="logs/plots_e2.log"

if ! [[ "$DESDE" =~ ^[0-9]+$ && "$HASTA" =~ ^[0-9]+$ ]]; then
    echo "DESDE/HASTA deben ser numeros de plot (ej. 01 28), se recibio: desde='$DESDE' hasta='$HASTA'" >&2
    exit 1
fi

if ! python3 -c "import numpy, pandas, xarray, netCDF4, scipy, matplotlib" 2>/dev/null; then
    echo "Al entorno de Python ($(command -v python3)) le faltan dependencias de los graficos de E2." >&2
    python3 -c "import numpy, pandas, xarray, netCDF4, scipy, matplotlib" 2>&1 | tail -1 >&2 || true
    echo "Actualizalo con: conda env update -n smn_toe -f environment.yml" >&2
    exit 1
fi

if ! ls data/processed/e2/indices_enso_????-????.csv >/dev/null 2>&1 \
   || ! ls data/processed/e2/skill_score_vent*m_*.csv >/dev/null 2>&1; then
    echo "Faltan resultados de E2 en data/processed/e2/ -- corré primero: bash rune2.sh" >&2
    exit 1
fi

echo "== rune2plot.sh: $(date '+%Y-%m-%d %H:%M:%S') (plots $DESDE..$HASTA) ==" | tee -a "$LOG_FILE"

FALLIDOS=()
for script in scripts_e2/plot[0-9][0-9]_*.py; do
    nn=$(basename "$script" | sed -E 's/^plot([0-9]{2})_.*/\1/')
    [ "$nn" = "00" ] && continue   # plot00_comun.py: helpers, no es una figura
    if [ $((10#$nn)) -lt $((10#$DESDE)) ] || [ $((10#$nn)) -gt $((10#$HASTA)) ]; then
        continue
    fi
    echo "== $(basename "$script") ==" | tee -a "$LOG_FILE"
    if ! python3 "$script" 2>&1 | tee -a "$LOG_FILE"; then
        FALLIDOS+=("$(basename "$script")")
        echo "  (fallo $(basename "$script") -- revisar el aviso arriba)" | tee -a "$LOG_FILE"
    fi
done

if [ "${#FALLIDOS[@]}" -gt 0 ]; then
    echo "== rune2plot.sh terminado con ${#FALLIDOS[@]} figura(s) fallida(s): ${FALLIDOS[*]} ==" | tee -a "$LOG_FILE"
    exit 1
fi
echo "== rune2plot.sh terminado: figuras en figures/e2/ ==" | tee -a "$LOG_FILE"
