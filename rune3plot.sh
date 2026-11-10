#!/usr/bin/env bash
# Figuras del Entregable 3: corre los scripts de graficos
# scripts_e3/plot<codigo>_<nombre>.py, en orden, sobre lo que rune3.sh ya
# dejo en data/processed/e3/. El codigo es el numero de la figura en el
# informe (e3_informe/informe_e3.tex):
#   cuerpo  01..09   plot05_cambio_sigma_por_modelo.py -> figures/e3/e3_05_cambio_sigma_por_modelo.png (Figura 5)
#   anexo   A01..A10 plotA09_espectro.py               -> figures/e3/e3_A09_espectro.png (Figura A9)
#
# Uso: bash rune3plot.sh [DESDE] [HASTA]
#   - Sin args: todas las figuras (01 ... A10).
#   - Con args: rango por codigo de figura, inclusive:
#       bash rune3plot.sh 05          -> solo la Figura 5
#       bash rune3plot.sh 01 09       -> las del cuerpo
#       bash rune3plot.sh A           -> todas las del anexo
#       bash rune3plot.sh A03 A05     -> A3..A5
#   - E3_GRUPO=40 bash rune3plot.sh   -> dibuja otro conjunto (15, 40, 11 o 7):
#     las figuras salen con sufijo _g40 y no se copian al informe.
#
# Salida: figures/e3/e3_<codigo>_<nombre>.png y, con el conjunto de 15,
# copia en e3_informe/figuras/ (la que usa informe_e3.tex). Log en
# logs/plots_e3.log. Una figura que falla no corta las demas; al final se
# listan las que fallaron y el script sale con error si hubo alguna.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p logs

# Argumentos leidos ANTES de activar conda (ver rune2plot.sh).
DESDE="${1:-01}"
HASTA="${2:-$DESDE}"
[ "$#" -eq 0 ] && HASTA="ZZ"

set +eu
if command -v conda >/dev/null 2>&1 && [ "$(basename "${CONDA_PREFIX:-}")" != "smn_toe" ]; then
    eval "$(conda shell.bash hook 2>/dev/null)" || true
    if conda env list 2>/dev/null | grep -qE '(^|[[:space:]])smn_toe([[:space:]]|$)'; then
        conda activate smn_toe 2>/dev/null || true
    fi
fi
set -eu
if [ -n "${CONDA_PREFIX:-}" ]; then
    export PATH="$CONDA_PREFIX/bin:$PATH"
fi
export PYTHONNOUSERSITE=1
export MPLBACKEND=Agg

LOG_FILE="logs/plots_e3.log"
CODIGO='^(A|A?[0-9]{2}|ZZ)$'
if ! [[ "$DESDE" =~ $CODIGO && "$HASTA" =~ $CODIGO ]]; then
    echo "DESDE/HASTA deben ser codigos de figura (ej. 05, A, A03), se recibio: desde='$DESDE' hasta='$HASTA'" >&2
    exit 1
fi
export LC_ALL=C   # orden ASCII: 01 < 09 < A < A01 < A10

if ! ls data/processed/e3/resumen_multimodelo_ref*.csv >/dev/null 2>&1; then
    echo "Faltan resultados de E3 en data/processed/e3/ -- correr primero: ./rune3.sh" >&2
    exit 1
fi

GRUPO="${E3_GRUPO:-15}"
echo "== rune3plot.sh: $(date '+%Y-%m-%d %H:%M:%S') (plots $DESDE..$HASTA, grupo $GRUPO) ==" | tee -a "$LOG_FILE"

FALLIDOS=()
for script in scripts_e3/plot[0-9A][0-9]*_*.py; do
    base=$(basename "$script" .py)
    code=$(echo "$base" | sed -E 's/^plot(A?[0-9]{2})_.*/\1/')
    [ "$code" = "00" ] && continue   # plot00_comun_e3.py: helpers, no es una figura
    # code >= DESDE y (code <= HASTA o code empieza con HASTA: "A" abarca A01..A10)
    [[ "$code" < "$DESDE" ]] && continue
    [[ "$code" > "$HASTA" && "$code" != "$HASTA"* ]] && continue
    echo "== $(basename "$script") ==" | tee -a "$LOG_FILE"
    if python3 "$script" 2>&1 | tee -a "$LOG_FILE"; then
        if [ "$GRUPO" = "15" ]; then
            png="e3_${base#plot}.png"
            cp "figures/e3/$png" "e3_informe/figuras/$png"
        fi
    else
        FALLIDOS+=("$(basename "$script")")
        echo "  (fallo $(basename "$script") -- revisar el aviso arriba)" | tee -a "$LOG_FILE"
    fi
done

if [ "${#FALLIDOS[@]}" -gt 0 ]; then
    echo "== rune3plot.sh terminado con ${#FALLIDOS[@]} figura(s) fallida(s): ${FALLIDOS[*]} ==" | tee -a "$LOG_FILE"
    exit 1
fi
echo "== rune3plot.sh terminado: figuras en figures/e3/ (copia del conjunto de 15 en e3_informe/figuras/) ==" | tee -a "$LOG_FILE"
