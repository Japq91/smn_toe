#!/usr/bin/env bash
# Uso: compilar_auditoria.sh A01 <fragmento1.tex> [fragmento2.tex ...]
# Cuenta palabras de los fragmentos propuestos, compila la auditoria
# (pdflatex x3 + bibtex) y reporta errores/warnings relevantes.
set -u
ID="$1"; shift
DIR=/home/jonathan/personal/e1_smn/revision_e1
n=0
for f in "$@"; do w=$(sed 's/%.*$//' "$DIR/informe/secciones/$f" | detex | wc -w); n=$((n+w)); done
echo "$n " > "$DIR/trabajo/conteo_${ID}.tex"
cd "$DIR/auditorias"
TEX=$(ls ${ID}_*.tex)
BASE=${TEX%.tex}
pdflatex -interaction=nonstopmode -halt-on-error "$TEX" > /dev/null
bibtex "$BASE" > /dev/null 2>&1
pdflatex -interaction=nonstopmode -halt-on-error "$TEX" > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error "$TEX" > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error "$TEX" > /dev/null
echo "palabras propuestas: $n"
grep -nE '^!|Fatal|Undefined|undefined|multiply defined|Overfull' "$BASE.log" | head -20
ls -la "$BASE.pdf" && pdfinfo "$BASE.pdf" | grep Pages
# limpiar auxiliares por nombre exacto
for e in aux log out toc bbl blg lof lot; do rm -f "$BASE.$e"; done
