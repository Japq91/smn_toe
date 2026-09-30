#!/usr/bin/env bash
cd /home/jonathan/personal/e1_smn/revision_e1
sleep 300
cd anexo && (pdflatex -interaction=nonstopmode anexo_uso_pipeline.tex; pdflatex -interaction=nonstopmode anexo_uso_pipeline.tex; pdflatex -interaction=nonstopmode anexo_uso_pipeline.tex) > /dev/null 2>&1
echo "anexo: $(grep -a -cE '^!|Overfull' anexo_uso_pipeline.log) problemas, $(pdfinfo anexo_uso_pipeline.pdf | awk '/Pages/{print $2}') págs"
for e in aux log out toc; do rm -f anexo_uso_pipeline.$e; done
cp anexo_uso_pipeline.pdf ../PDF/B02_anexo_uso_pipeline.pdf
echo "ANEXO v3 $(date '+%F %T')" >> ../trabajo/bitacora_generacion.txt
cd ../trabajo
for x in "A01 01_resumen_alcance.tex" "A02 02_antecedentes_literatura.tex" "A04 04_datos.tex" "A05 05_arquitectura.tex" "A06 06_pasos.tex" "A08 08_cierre.tex"; do
  sleep 300; id=${x%% *}
  ./compilar_auditoria.sh $x | grep -v "^-rw"
  cp ../auditorias/${id}_*.pdf ../PDF/
  echo "$id v3 $(date '+%F %T')" >> bitacora_generacion.txt
done
echo FIN
