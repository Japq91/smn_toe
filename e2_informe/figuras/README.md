# e2_informe/figuras/

Symlinks curados a `figures/e2/*.png`, mismo criterio que
`e1_informe/figuras/` para el Entregable 1: solo los archivos que el
`e2_informe/informe_e2.tex` referencia de verdad (`figuras/<archivo>.png`
en el `.tex`), no todo `figures/e2/`. Agregar un symlink nuevo con:

```
ln -sf ../../figures/e2/<archivo>.png e2_informe/figuras/<archivo>.png
```
