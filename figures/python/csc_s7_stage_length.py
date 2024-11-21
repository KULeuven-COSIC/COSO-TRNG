"""Generate obtained C values for different number of RO stages and omitted GP and LP constraints
figure for Spartan 7."""
import argparse
import sys
import csv
import itertools as it
from os import getcwd
from os.path import join, isfile
from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'no_placement_s7')

RO_NAMES: List[str] = ['GateVar', 'WireVar', 'LUTVar0', 'LUTVar5']
RO_TYPES: List[str] = ['muxnetwork', 'wireonly', 'intralut0', 'intralut5']

STAGE_LENGTHS: List[int] = [1, 2, 3, 4]

CSC_THRESH = 59.0

X_LIM = (0.5, (len(RO_TYPES) + 1) * len(STAGE_LENGTHS) - 0.5)
Y_LIM = (0.4, 9e4)

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = s_d.StoreData(name='csc_s7_stage_length')

cscs: Dict[str, Dict[int, List[float]]] = {}
if args.d:
    # Parse CSV files:
    for ro_type, stage_length in it.product(RO_TYPES, STAGE_LENGTHS):
        file_name = join(DATA_FOLDER, ro_type + '_np',
                         f'all_configs_{ro_type}_np_coso_x0y0_stages{stage_length}.csv')
        if not isfile(file_name):
            if args.v:
                print(f'File: {file_name} does not exist!')
            continue
        cs: List[float] = []
        with open(file_name, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                cs.append(float(row[4]))
        if not cs:
            if args.v:
                print(f'File: {file_name} is empty!')
            continue
        for c_i in range(len(cs) - 1, -1, -1):
            if cs[c_i] <= 0:
                del cs[c_i]
        if args.v:
            print(f'{ro_type}, {stage_length} stages: # CSC: {len(cs)}')
        if ro_type not in cscs:
            cscs[ro_type] = {}
        cscs[ro_type][stage_length] = cs

    # Print out stats:
    if args.v:
        for ro_type, cs_ro in cscs.items():
            for stage_length, cs in cs_ro.items():
                print(f'{ro_type}, {stage_length} stages: mean CSC = {np.mean(cs)}, '
                      f'var CSC = {np.var(cs)}')

    data_to_write: List[List[float]] = []
    for ro_type in RO_TYPES:
        if ro_type in cscs:
            for stage_length in STAGE_LENGTHS:
                if stage_length in cscs[ro_type]:
                    data_to_write.append(cscs[ro_type][stage_length])
                else:
                    data_to_write.append([])
        else:
            data_to_write.append([])
    store_data.write_data(data_to_write, True)
    if args.q:
        sys.exit()
else:
    if not store_data.file_exist:
        if args.v:
            print(f'No data was stored at: {store_data.file_path}')
        sys.exit()
    data = store_data.read_data()
    if data is None:
        if args.v:
            print(f'No data was stored at: {store_data.file_path}')
        sys.exit()
    for d, (ro_type, stage_length) in zip(data, it.product(RO_TYPES, STAGE_LENGTHS)):
        if ro_type not in cscs:
            cscs[ro_type] = {}
        cscs[ro_type][stage_length] = d

if args.v:
    for i, (stage_length, ro_type) in enumerate(it.product(STAGE_LENGTHS, RO_TYPES)):
        plt.boxplot(cscs[ro_type][stage_length], positions=[i]) # type: ignore
    plt.gca().set_yscale('log') # type: ignore
    plt.show() # type: ignore

graph_maker = g_m.GraphMaker('csc_s7_stage_length.svg', figure_size=(1, 1),
                             folder_name='figures', figure_height_scale=0.85)
graph_maker.create_grid(size=(1, 1), marg_top=0.88, marg_bot=0.34)

x_label_locs: List[float] = [s_i * (len(RO_TYPES) + 1) + r_i + 1
                             for s_i, _ in enumerate(STAGE_LENGTHS)
                             for r_i, _ in enumerate(RO_TYPES)]
x_labels = [RO_NAMES[i % 4] for i in range(len(RO_TYPES) * len(STAGE_LENGTHS))]

ax = graph_maker.create_ax(x_slice=0, y_slice=0, # pylint: disable=invalid-name
                           title='Obtainable $C$ values versus number of stages',
                           x_label='RO topology', y_label='$C$',
                           x_unit='-', y_unit='-',
                           y_scale='log10', x_scale='fix',
                           y_grid=True,
                           fixed_locs_x=x_label_locs,
                           fixed_labels_x=x_labels,
                           x_lim=X_LIM, y_lim=Y_LIM,
                           x_label_rotate=45)

# Plot gradient:
graph_maker.fill_between_y(ax=ax, xs=list(X_LIM), y0s=[CSC_THRESH] * 2,
                           y1s=[Y_LIM[1]] * 2, color='white', grad_end_color=2,
                           grad_hor=False, grad_log=True)

# Plot data:
for pos_i, (stage_length, ro_type) in zip(x_label_locs, it.product(STAGE_LENGTHS, RO_TYPES)):
    graph_maker.violin(ax=ax, data=cscs[ro_type][stage_length], color=0,
                       position=int(pos_i),
                       show_box=True, marker='dot', hist=False,
                       marker_color=1, median_color=1)

# Generate stages text:
for stage_length in STAGE_LENGTHS:
    graph_maker.text(ax=ax, x=(len(RO_TYPES) + 1) * (stage_length - 0.5), y=Y_LIM[1] / 3,
                     s=f'{stage_length} stage{"s" if stage_length > 1 else ""}',
                     border_color='white')

# Generate SVG:
graph_maker.write_svg()
