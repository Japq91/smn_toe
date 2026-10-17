#!/bin/bash
BASE_DIR="."
DEST_DIR="./files_MD"

if ! command -v markitdown &> /dev/null; then
    echo "Error: markitdown no está instalado o no está en el PATH"
    exit 1
fi

mkdir -p "$DEST_DIR"

for grupo_dir in "$BASE_DIR"/files_pdf*; do
    if [ -d "$grupo_dir" ]; then
        echo "Procesando: $grupo_dir"
        for pdf_file in "$grupo_dir"/*.pdf "$grupo_dir"/*.PDF; do
            if [ -f "$pdf_file" ]; then
                basename=$(basename "$pdf_file" .pdf)
                basename=$(basename "$basename" .PDF)
                output_file="$DEST_DIR/${basename}.md"

                if [ -f "$output_file" ]; then
                    echo "  Omitiendo: ${basename}.md ya existe"
                    continue
                fi

                echo "  Convirtiendo: $(basename "$pdf_file") -> ${basename}.md"
                markitdown "$pdf_file" -o "$output_file"

                if [ $? -eq 0 ]; then
                    echo "    ✓ Conversión exitosa"
                else
                    echo "    ✗ Error en la conversión"
                fi
            fi
        done
    fi
done

echo "Proceso completado. Archivos .md guardados en: $DEST_DIR"
