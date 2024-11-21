"""Generate obtained C values without specified GP and LP constraints on a heavily congested
FPGA figure for Spartan 7."""
import argparse
import sys
import csv
from os import getcwd
from os.path import join, isfile
from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'no_placement_congestion_s7')

RO_NAMES: List[str] = ['GateVar', 'WireVar', 'LUTVar0', 'LUTVar5']
RO_TYPES: List[str] = ['muxnetwork', 'wireonly', 'intralut0', 'intralut5']

STAGES: int = 4

CSC_THRESH = 59.0

X_LIM = (0.5, 4.5)
Y_LIM = (0.07, 9e3)

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = s_d.StoreData(name='csc_s7_no_placement_congest')

cscs: Dict[str, List[float]] = {}
if args.d:
    # Parse CSV files:
    for ro_type in RO_TYPES:
        file_name = join(DATA_FOLDER, ro_type + '_np_cg',
                         (f'all_configs_{ro_type}_np_congest'
                          f'_coso_x0y0_stages{STAGES}.csv'))
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
            print(f'{ro_type}: '
                  f'# CSC: {len(cs)}')
        cscs[ro_type] = cs

    # Print out stats:
    if args.v:
        for ro_type, cs in cscs.items():
            print(f'{ro_type}: mean CSC = {np.mean(cs)}, var CSC = {np.var(cs)}')

    data_to_write: List[List[float]] = []
    for ro_type in RO_TYPES:
        if ro_type in cscs:
            data_to_write.append(cscs[ro_type])
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
    for d, ro_type in zip(data, RO_TYPES):
        cscs[ro_type] = d

if args.v:
    for i, (ro_type, cs) in enumerate(cscs.items()):
        plt.boxplot(cs, positions=[i]) # type: ignore
    plt.gca().set_yscale('log') # type: ignore
    plt.show() # type: ignore

graph_maker = g_m.GraphMaker('csc_s7_no_placement_congest.svg', figure_size=(1, 1),
                             folder_name='figures', figure_height_scale=0.75)
graph_maker.create_grid(size=(1, 1), marg_top=0.85, marg_bot=0.2, marg_left=0.11)

ax = graph_maker.create_ax(x_slice=0, y_slice=0, # pylint: disable=invalid-name
                           title='Obtainable $C$ values, congested',
                           x_label='RO topology', y_label='$C$',
                           x_unit='-', y_unit='-',
                           y_scale='log10', x_scale='fix',
                           y_grid=True,
                           fixed_locs_x=[1, 2, 3, 4],
                           fixed_labels_x=RO_NAMES,
                           x_lim=X_LIM, y_lim=Y_LIM)

# Plot gradient:
graph_maker.fill_between_y(ax=ax, xs=list(X_LIM), y0s=[CSC_THRESH] * 2,
                           y1s=[Y_LIM[1]] * 2, color='white', grad_end_color=2,
                           grad_hor=False, grad_log=True)

# Plot data:
for pos_i, (cs, ro_name) in enumerate(zip(cscs.values(), RO_NAMES)):
    graph_maker.violin(ax=ax, data=cs, color=0, position=pos_i + 1,
                       show_box=True, marker='dot', hist=False,
                       marker_color=1, median_color=1)

# Generate SVG:
graph_maker.write_svg()
