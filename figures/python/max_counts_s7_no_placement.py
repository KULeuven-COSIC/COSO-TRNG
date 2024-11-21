"""Generate controller latency for variable upper bound figure for Spartan 7."""
import argparse
import sys
import csv
import itertools as it
from os import getcwd
from os.path import join, isfile
from typing import List, Dict, Tuple, cast
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'no_placement_matched_control_s7')

RO_NAMES: List[str] = ['GateVar', 'WireVar']
RO_TYPES: List[str] = ['muxnetwork', 'wireonly']

STAGES_LENGTHS: List[int] = [3, 4]

MARKERS: List[str] = ['circle', 'cross', 'square', 'tri_up']

Y_LIM = (1e-4, 1e-1)

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = s_d.StoreData(name='max_counts_s7_no_placement')

lats: Dict[str, Dict[int, Tuple[List[int], List[float]]]] = {}
if args.d:
    # Parse CSV files:
    for ro_type, stage_length in it.product(RO_TYPES, STAGES_LENGTHS):
        file_name = join(DATA_FOLDER, ro_type + '_np_mc',
                         (f'maco_scan_{ro_type}_np'
                          f'_coso_stages{stage_length}.csv'))
        if not isfile(file_name):
            if args.v:
                print(f'File: {file_name} does not exist!')
            continue
        ls: List[float] = []
        ms: List[int] = []
        with open(file_name, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                ms.append(int(row[0]))
                ls.append(float(row[1]) * 10e-9)
        if not ls:
            if args.v:
                print(f'File: {file_name} is empty!')
            continue
        if ro_type not in lats:
            lats[ro_type] = {}
        lats[ro_type][stage_length] = (ms, ls)

    data_to_write: List[List[float]] = []
    for ro_type, stage_length in it.product(RO_TYPES, STAGES_LENGTHS):
        if ro_type in lats:
            if stage_length in lats[ro_type]:
                data_to_write.append(cast(List[float], lats[ro_type][stage_length][0]))
                data_to_write.append(lats[ro_type][stage_length][1])
            else:
                data_to_write.append([])
                data_to_write.append([])
        else:
            data_to_write.append([])
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
    for ms_f, ls_d, (ro_type, stage_length) in zip(data[::2], data[1::2],
                                               it.product(RO_TYPES, STAGES_LENGTHS)):
        ms_d = [int(d) for d in ms_f]
        if ro_type not in lats:
            lats[ro_type] = {}
        lats[ro_type][stage_length] = (ms_d, ls_d)

if args.v:
    for marker, (ro_type, stage_length) in zip(MARKERS, it.product(RO_TYPES, STAGES_LENGTHS)):
        plt.plot(lats[ro_type][stage_length][0], lats[ro_type][stage_length][1], 'o') # type: ignore
    plt.gca().set_yscale('log') # type: ignore
    plt.show() # type: ignore

graph_maker = g_m.GraphMaker('max_counts_s7_no_placement.svg', figure_size=(1, 1),
                             folder_name='figures', figure_height_scale=0.75)
graph_maker.create_grid(size=(1, 1), marg_top=0.85, marg_bot=0.2, marg_left=0.11)

ax = graph_maker.create_ax(x_slice=0, y_slice=0, # pylint: disable=invalid-name
                           title='Controller latency, variable upper $C$ bound',
                           x_label='Upper $C$ bound ($h$)', y_label='Controller latency',
                           x_unit='-', y_unit='s',
                           y_scale='log10',
                           y_grid=True,
                           y_lim=Y_LIM,
                           show_legend=True,
                           leg_font_size=0.75)

# Plot data:
for color, (marker, ((ro_type, ro_name), stage_length)) \
    in enumerate(zip(MARKERS, it.product(zip(RO_TYPES, RO_NAMES), STAGES_LENGTHS))):
    ms, ls = lats[ro_type][stage_length]
    graph_maker.plot(ax=ax, xs=cast(List[float], ms), ys=ls, line_style='none',
                     marker=marker, label=f'{ro_name}, {stage_length} stages', alpha=1,
                     line_width=0.4, marker_color=color, edge_alpha=0,
                     color=color)

# Generate SVG:
graph_maker.write_svg()
