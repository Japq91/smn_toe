#!/usr/bin/env bash
# Recompila las auditorias afectadas por las decisiones del 29-09, con 5 min entre cada una.
cd /home/jonathan/personal/e1_smn/revision_e1/trabajo
for x in "A01 01_resumen_alcance.tex" "A03 03_ninos_metodos_toe.tex" "A04 04_datos.tex" "A05 05_arquitectura.tex" "A06 06_pasos.tex" "A07 07_resultados.tex" "A08 08_cierre.tex" "A10" "A00"; do
  sleep 300
  id=${x%% *}
  if [ "$id" = "A00" ]; then
    t=0; for k in 01 02 03 04 05 06 07 08; do t=$((t+$(cat conteo_A$k.tex))); done
    printf "%d\\\\,%03d" $((t/1000)) $((t%1000)) > conteo_total.tex
    { for f in ../PDF/A*.pdf ../PDF/B*.pdf; do b=$(basename "$f"); n=$(pdfinfo "$f" | awk '/Pages/{print $2}'); case $b in A00*) n="--";; esac
        d=$(case $b in A00*) echo "Este resumen";; A01*) echo "Portada, Resumen, Alcance";; A02*) echo "Antecedentes y literatura sobre TOE";; A03*) echo "Niño~3.4 frente a Niño~1+2; métodos M1 y ToD";; A04*) echo "Fuentes, modelos, selección, dominios y periodos";; A05*) echo "Arquitectura y \\texttt{run.sh}";; A06*) echo "Pasos 00--07 (detalle ahora en el anexo)";; A07*) echo "Resultados y figuras";; A08*) echo "Próximos pasos, conclusiones, recomendaciones";; A09*) echo "Bibliografía y citas";; A10*) echo "Compilación, formato y cierre del repositorio";; B01*) echo "\\textbf{Informe revisado del Entregable~1}";; B02*) echo "\\textbf{Anexo: guía de uso y detalle de los pasos}";; esac)
        echo "\\archivo{$b} & $d & $n \\\\"; done; } > tabla_paginas.tex
    echo "0 " > conteo_A00.tex
    ./compilar_auditoria.sh A00
  elif [ "$id" = "A10" ]; then echo "0 " > conteo_A10.tex; ./compilar_auditoria.sh A10
  else ./compilar_auditoria.sh $x; fi
  cp ../auditorias/${id}_*.pdf ../PDF/
  echo "$id v2 $(date '+%F %T')" >> bitacora_generacion.txt
done
echo FIN
