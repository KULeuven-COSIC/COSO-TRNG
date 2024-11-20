# Figure generation folder

This folder contains the necessary scripts to generate the figures, visualizing the data in the *measurements/* and *math_mode/results/* folders.

## Usage

Use the provided *makefile* to generate figure PDFs.
The following make targets are available:
- `all` or `pdf`: Generate all PDFs.
- `svg`: Generate all SVGs.
- `[figure name].pdf`: Only generate *[figure name].pdf*.
- `clean`: Remove PDFs.
- `realclean`: Remove all generated files: PDFs, SVGs and CSVs.

## Note

Many figure generation scripts store processed data in the *data/* folder.
Using this processed data allows for faster figure regeneration.