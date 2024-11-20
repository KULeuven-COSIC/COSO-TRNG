PY_DIR := figures/python/
SVG_DIR := figures/svg/
PDF_DIR := figures/pdf/
DAT_DIR := figures/data/

PY_FILES := $(shell find $(PY_DIR) -type f -name "*.py")
SVG_FILES := $(shell find $(SVG_DIR) -type f -name "*.svg")

PY_SVGS := $(addprefix $(SVG_DIR), $(addsuffix .svg, $(basename $(notdir $(PY_FILES)))))

PY_PDFS := $(addprefix $(PDF_DIR), $(addsuffix .pdf, $(basename $(notdir $(PY_FILES)))))
SVG_PDFS := $(addprefix $(PDF_DIR), $(addsuffix .pdf, $(basename $(notdir $(SVG_FILES)))))

all: pdf

pdf: $(PDF_DIR) $(PY_PDFS) $(SVG_PDFS)

svg: $(SVG_DIR) $(PY_SVGS)

$(PDF_DIR)%.pdf: $(SVG_DIR) $(SVG_DIR)%.svg
	rsvg-convert -f pdf -o $@ $(SVG_DIR)$*.svg

$(SVG_DIR)%.svg: $(PY_DIR)%.py $(DAT_DIR) $(DAT_DIR)%.csv
	python3 $<

$(DAT_DIR)%.csv: $(PY_DIR)%.py
	python3 $< -dq

.PRECIOUS: $(DAT_DIR) $(DAT_DIR)%.csv

%/:
	mkdir $@

%.pdf: $(PDF_DIR)%.pdf
	touch $@

clean: clean_pdf

realclean: clean_pdf clean_data clean_svg

clean_pdf:
	rm -f $(PY_PDFS) $(SVG_PDFS)
	rm -df $(PDF_DIR)

clean_svg:
	rm -f $(addprefix $(SVG_DIR), $(addsuffix .svg, $(basename $(notdir $(PY_FILES)))))
	rm -df $(SVG_DIR)

clean_data:
	rm -f $(addprefix $(DAT_DIR), $(addsuffix .csv, $(basename $(notdir $(PY_FILES)))))
	rm -df $(DAT_DIR)

modeldata:
	python3 math_model/generate_h_vs_csc.py