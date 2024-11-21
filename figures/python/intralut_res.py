"""Generate intra LUT resolution on Spartan 7 figure."""
import argparse
import sys
import csv
from typing import List
from os.path import join
import numpy as np
import drawSvg as draw # type: ignore # pylint: disable=import-error

RO_TYPES = (0, 1, 2, 3, 4, 5)
STAGES = (1, 2, 3, 4)
LOC_X = 0
LOC_Y = 0

# Graphical parameters:
MM_DELAY = (0, 10)
BOX_Y = (25, 103)
BOX_X = (25, 25 + len(STAGES) * (len(RO_TYPES) * 12 + 10))

MEAS_FOLDER = 'measurements/lp_variable_gp_s7'

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Collect data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

if args.d:
    if args.q:
        sys.exit()

# Create canvas:
d = draw.Drawing(BOX_X[1] + 17, BOX_Y[1] + 15, displayInline=False)

# Draw back plane:
d.append(draw.Lines(0, 0, 0, BOX_Y[1] + 15, BOX_X[1] + 17, # type: ignore
                    BOX_Y[1] + 15, BOX_X[1] + 17, 0,
                    close=True, stroke_width=0, fill='white'))

# Draw outside border
d.append(draw.Lines(BOX_X[0], BOX_Y[1], BOX_X[1], BOX_Y[1], # type: ignore
                    BOX_X[1], BOX_Y[0], BOX_X[0], BOX_Y[0],
                    close=True, stroke='black', stroke_width=0.5, fill='white'))

for rt, r_type in enumerate(RO_TYPES):
    for st, stage in enumerate(STAGES):
        file_name = join(MEAS_FOLDER, f'intralut{r_type}',
                         f'all_configs_intralut{r_type}_x{LOC_X}y{LOC_Y}_stages{stage}.csv')
        delays: List[float] = []
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f, delimiter=',')
                next(csv_reader)
                for row in csv_reader:
                    delays.append(float(row[1]))
        except FileNotFoundError:
            if args.v:
                print(f'file does not exist: type={r_type}, stage={stage}')
            continue
        if not delays:
            if args.v:
                print(f'length zero{stage}, {r_type}')
            continue
        d_s = list(delays)
        d_s.sort()
        resol: List[float] = []
        for i in range(len(d_s) - 1):
            resol.append(d_s[i + 1] - d_s[i])
        for i in range(len(resol) - 1, -1, -1):
            if resol[i] == 0:
                del resol[i]
        med_resol = 10 - np.median(resol) * 10000

        per = np.mean(delays)
        measurement_acc = 10 - (per - 1307540 / (1307540 / per + 1)) * 10000
        bar_color_0 = 'blue' # pylint: disable=invalid-name
        bar_color_1 = '#85c1e9' # pylint: disable=invalid-name
        if med_resol > measurement_acc:
            if args.v:
                print(f'hit measurement limit {stage} {r_type}')
            med_resol = measurement_acc
            bar_color_0 = '#d35400' # pylint: disable=invalid-name
            bar_color_1 = '#f8c471' # pylint: disable=invalid-name

        mid_x = BOX_X[0] + 11 + rt * 12 + st * (len(RO_TYPES) * 12 + 10)
        posi = 1 # pylint: disable=invalid-name

        # Draw axis tabs
        d.append(draw.Lines(mid_x, BOX_Y[0], mid_x, BOX_Y[0] + 5, # type: ignore
                            close=False, stroke='black', stroke_width=0.5))
        d.append(draw.Lines(mid_x, BOX_Y[1], mid_x, BOX_Y[1] - 5, # type: ignore
                            close=False, stroke='black', stroke_width=0.5))

        # Draw X labels
        d.append(draw.Text(str(r_type), 7, mid_x, BOX_Y[0] - 8, # type: ignore
                           fill='black', **{'text-anchor': 'middle'})) # type: ignore

        # Draw bars:
        d.append(draw.Lines(mid_x - 6, BOX_Y[0], mid_x - 6, # type: ignore
                            (med_resol - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            mid_x + 6,
                            (med_resol - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            mid_x + 6, BOX_Y[0], close=False, stroke=bar_color_0,
                            stroke_width=1, fill=bar_color_1))


# Draw Y tabs and labels
for i in range(int(np.ceil(MM_DELAY[0])), int(np.ceil(MM_DELAY[1])) + 1, 1):
    j = i
    if i % 2 == 0:
        d.append(draw.Lines(BOX_X[0], # type: ignore
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            BOX_X[0] + 5,
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            close=False, stroke='black', stroke_width=0.5))
        d.append(draw.Lines(BOX_X[1], # type: ignore
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            BOX_X[1]-5,
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            close=False, stroke='black', stroke_width=0.5))
        text = str((10 - i) / 10) # pylint: disable=invalid-name
        d.append(draw.Text(text, 7, # type: ignore
                           BOX_X[0] - 3, (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0] - 3,
                           **{'text-anchor': 'end'})) # type: ignore
        d.append(draw.Text(text, 7, # type: ignore
                           BOX_X[1] + 3, (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0] - 3,
                           **{'text-anchor': 'start'})) # type: ignore
    else:
        d.append(draw.Lines(BOX_X[0], # type: ignore
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            BOX_X[0] + 2.5,
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            close=False, stroke='black', stroke_width=0.5))
        d.append(draw.Lines(BOX_X[1], # type: ignore
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            BOX_X[1] - 2.5,
                            (j - MM_DELAY[0]) / (MM_DELAY[1] - MM_DELAY[0]) \
                                * (BOX_Y[1] - BOX_Y[0]) + BOX_Y[0],
                            close=False, stroke='black', stroke_width=0.5))

# Draw Y label:
d.append(draw.Text('Resolution [ps]', 7, 10, # type: ignore
                   int(BOX_Y[0] / 2 + BOX_Y[1] / 2),
                   transform=f'rotate(-90, {10}, {-int(BOX_Y[0]/2+BOX_Y[1]/2)})',
                   **{'text-anchor': 'middle'})) # type: ignore

# Draw X label:
d.append(draw.Text('Physical input port number [-]', 7, # type: ignore
                   BOX_X[0]/2+BOX_X[1]/2, 10,
                   **{'text-anchor': 'middle'})) # type: ignore

# Draw top X labels:
for i, stage_i in enumerate(STAGES):
    mid = int(BOX_X[0] + (len(RO_TYPES) * 12 + 10) * (i + 1 / 2))
    stages = ' stages' # pylint: disable=invalid-name
    if stage_i == 1:
        stages = ' stage' # pylint: disable=invalid-name
    d.append(draw.Text(str(stage_i) + stages, 10, mid, BOX_Y[1]+5, # type: ignore
                       **{'text-anchor': 'middle'})) # type: ignore

d.saveSvg('figures/svg/intralut_res.svg') # type: ignore
