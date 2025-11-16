The files in this directory are the ones that were used to generate circuit files seem through the docs. To generate
them, you'll need some latex compiler, that contains the circuitikz package.

For livetex, together with imagemagick, you can generate the pngs for each circuit with the following command:

```
NAME=<file_base_path>; pdflatex "$NAME".tex; magick -density 600 "$NAME".pdf -quality 100 -background white -alpha remove -bordercolor white -border 50 "$NAME".png
```

Substituting `<file_base_path>` with the base name for the file you want to compile (without the .tex extension), like
`rlc_circuit`, for compiling `rlc_circuit.tex`.
