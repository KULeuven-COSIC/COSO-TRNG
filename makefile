PY_DIR := figures/python/
SVG_DIR := figures/svg/
PDF_DIR := figures/pdf/
DAT_DIR := figures/data/

PY_FILES := $(shell find $(PY_DIR) -type f -name "*.py")
SVG_FILES := $(shell find $(SVG_DIR) -type f -name "*.svg")

PY_PDFS := $(addprefix $(PDF_DIR), $(addsuffix .pdf, $(basename $(notdir $(PY_FILES)))))
SVG_PDFS := $(addprefix $(PDF_DIR), $(addsuffix .pdf, $(basename $(notdir $(SVG_FILES)))))

all: pdf

pdf: $(PY_PDFS) $(SVG_PDFS)

$(PDF_DIR)%.pdf: $(SVG_DIR)%.svg
	rsvg-convert -f pdf -o $@ $<

$(SVG_DIR)%.svg: $(PY_DIR)%.py $(DAT_DIR)%.csv
	python3 $<

$(DAT_DIR)%.csv: $(PY_DIR)%.py
	python3 $< -dq

.PRECIOUS: $(DAT_DIR)%.csv

clean: clean_pdf

realclean: clean_pdf clean_data clean_svg

clean_pdf:
	rm -f $(PY_PDFS) $(SVG_PDFS)

clean_svg:
	rm -f $(addprefix $(SVG_DIR), $(addsuffix .svg, $(basename $(notdir $(PY_FILES)))))

clean_data:
	rm -f $(addprefix $(DAT_DIR), $(addsuffix .csv, $(basename $(notdir $(PY_FILES)))))