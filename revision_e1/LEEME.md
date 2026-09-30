# Revisión del informe del Entregable 1 (28-09-2026)

Carpeta local, excluida de git mediante `.git/info/exclude`. No se sube a GitHub.

## Para leer

`PDF/` contiene todos los documentos finales:

- `A00_resumen_consolidado.pdf`: empezar por aquí (113 hallazgos, decisiones pendientes).
- `A01` a `A10`: una auditoría por tema, cada una con sus hallazgos y el texto corregido.
- `B01_informe_e1_revisado.pdf`: informe nuevo del Entregable 1 (23 páginas).
- `B02_anexo_uso_pipeline.pdf`: anexo con la guía de uso de `run.sh` y el detalle de cada paso (12 páginas).

## Fuentes (para editar)

- `informe/informe_e1_revisado.tex` y `informe/secciones/*.tex`: una sección por auditoría.
- `informe/references_rev.bib`: bibliografía corregida (el `informe/references.bib` original no se tocó).
- `anexo/anexo_uso_pipeline.tex`
- `trabajo/macros_informe.tex`: fecha de la portada (`\fechaentrega`) y commit del E1.
- `figuras/`: figuras reales (no enlaces simbólicos); mapas 2D y mapa de regiones con la ventana vigente (0°–360°, 30°S–30°N).
- `trabajo/e1_snapshot/`: copia de `scripts/` y `config/` del commit `8ee6184`, con las correcciones de gráficos probadas.

## Recompilar

Informe (4 pasadas de pdflatex, necesarias por longtable + hyperref):

    cd informe && pdflatex informe_e1_revisado && bibtex informe_e1_revisado \
      && pdflatex informe_e1_revisado && pdflatex informe_e1_revisado && pdflatex informe_e1_revisado

Una auditoría: `trabajo/compilar_auditoria.sh A03 03_ninos_metodos_toe.tex`

## Orden de generación

Registro en `trabajo/bitacora_generacion.txt`, con al menos 5 minutos entre documentos.

## Actualización del 29-09-2026

- La Sección 6 del informe se redujo a un párrafo más el flujograma; el detalle de cada paso está en el anexo (`trabajo/anexo_pasos.tex`).
- Ventana de descarga vigente (0°–360°, 30°S–30°N) y techo del control de calidad en 45 °C.
- El informe no cita commits y el repositorio se presenta como de libre acceso.
