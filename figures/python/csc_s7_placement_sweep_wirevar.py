"""Generate calculated C values using the WireVar topology at 25 different locations figure."""
import argparse
import sys
import csv
import itertools as it
from os import getcwd
from os.path import join, isfile
from typing import List, Dict, Tuple
from pylfsr import LFSR # type: ignore # pylint: disable=import-error
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'lp_variable_gp_s7')

RO_NAME = 'WireVar'
RO_TYPE = 'wireonly'

X_LOCS = [0, 10, 28, 36, 52]
Y_LOCS = [0, 37, 74, 111, 148]
Y_LOCS_S = [1, 38, 75, 112, 147]
STAGES: int = 3

MAX_NB_CSC: int = 2**15

CSC_THRESH = 59.0

X_LIM = (0.5, 25.5)
Y_LIM = (0.7, 1.5e4)

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = s_d.StoreData(name='csc_s7_placement_sweep_wirevar')

cscs: Dict[Tuple[int, int], List[float]] = {}
if args.d:
    def bi2nu(bi: List[int]) -> int:
        """Binary to decimal."""
        result: int = 0
        for i_, b in enumerate(bi):
            result += b * 2**(i_)
        return result

    # Parse CSV files:
    for x_loc, (y_loc, y_loc_s) in it.product(X_LOCS, zip(Y_LOCS, Y_LOCS_S)):
        file_name = join(DATA_FOLDER, RO_TYPE,
                         f'all_configs_{RO_TYPE}_x{x_loc}y{y_loc}_'
                         f'stages{STAGES}.csv')
        file_name_s = join(DATA_FOLDER, RO_TYPE + '_s',
                         f'all_configs_{RO_TYPE}_s_x{x_loc}y{y_loc_s}_'
                         f'stages{STAGES}.csv')
        if not isfile(file_name):
            if args.v:
                print(f'File: {file_name} does not exist!')
            continue
        if not isfile(file_name_s):
            if args.v:
                print(f'File: {file_name_s} does not exist!')
            continue
        d_0s: List[float] = []
        d_1s: List[float] = []
        with open(file_name, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                d_0s.append(float(row[1]))
        with open(file_name_s, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                d_1s.append(float(row[1]))
        if not d_0s:
            if args.v:
                print(f'File: {file_name} is empty!')
            continue
        if not d_1s:
            if args.v:
                print(f'File: {file_name_s} is empty!')
            continue
        cscs_read: List[float] = []
        if len(d_0s) * len(d_1s) > MAX_NB_CSC:
            nb_db_0 = int(np.log2(len(d_0s)))
            nb_db_1 = int(np.log2(len(d_1s)))
            if (nb_db_0 + nb_db_1 != 40) & (nb_db_0 + nb_db_1 != 30):
                if args.v:
                    print(f'({x_loc}, {y_loc}), # bits is not 40 or 30: {nb_db_0 + nb_db_1}')
                continue
            if nb_db_0 + nb_db_1 == 40:
                fpoly: List[int] = [40, 37, 36, 35]
            else:
                fpoly = [30, 29, 26, 24]
            L = LFSR(fpoly=fpoly, initstate=[0] * (nb_db_0 + nb_db_1 - 1) + [1], # type: ignore
                     verbose=False)
            for i in range(MAX_NB_CSC):
                d0 = d_0s[bi2nu(L.state[0:nb_db_0])] # type: ignore
                d1 = d_1s[bi2nu(L.state[nb_db_0:nb_db_0 + nb_db_1])] # type: ignore
                if d0 == d1:
                    continue
                cscs_read.append(abs(d0 / (d1 - d0)))
                L.next() # type: ignore
        else:
            for d0, d1 in it.product(d_0s, d_1s):
                if d0 == d1:
                    continue
                cscs_read.append(abs(d0 / (d1 - d0)))
        if not cscs_read:
            if args.v:
                print(f'({x_loc}, {y_loc}): CSCs is empty!')
            continue
        if args.v:
            print(f'({x_loc}, {y_loc}): # RO0: {len(d_0s)}, # RO1: {len(d_1s)}, '
                  f'# CSC: {len(cscs_read)}, '
                  f'# dropped: {len(d_0s) * len(d_1s) - len(cscs_read)}')
        cscs[(x_loc, y_loc)] = cscs_read

    data_to_write: List[List[float]] = []
    for x_loc, y_loc in it.product(X_LOCS, Y_LOCS):
        if (x_loc, y_loc) in cscs:
            data_to_write.append(cscs[(x_loc, y_loc)])
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
    for d, (x_loc, y_loc) in zip(data, it.product(X_LOCS, Y_LOCS)):
        cscs[(x_loc, y_loc)] = d

if args.v:
    for i, ((x_loc, y_loc), cs) in enumerate(cscs.items()):
        plt.boxplot(cs, positions=[i]) # type: ignore
    plt.gca().set_yscale('log') # type: ignore
    plt.show() # type: ignore

graph_maker = g_m.GraphMaker('csc_s7_placement_sweep_wirevar.svg', figure_size=(1, 1),
                             folder_name='figures', figure_height_scale=0.85)
graph_maker.create_grid(size=(1, 1), marg_bot=0.41, marg_top=0.88)

x_label_locs: List[float] = list(range(1, len(X_LOCS) * len(Y_LOCS) + 1))
x_labels = [f'[{x_loc},{y_loc}]' for x_loc, y_loc in it.product(X_LOCS, Y_LOCS)]

ax = graph_maker.create_ax(x_slice=0, y_slice=0, # pylint: disable=invalid-name
                           title=f'Calculated $C$ values at 25 locations, {RO_NAME}',
                           x_label='FPGA location', y_label='$C$',
                           x_unit='x,y', y_unit='-',
                           y_scale='log10', x_scale='fix',
                           y_grid=True,
                           fixed_locs_x=x_label_locs,
                           fixed_labels_x=x_labels,
                           x_label_rotate=90,
                           x_lim=X_LIM, y_lim=Y_LIM)

# Plot gradient:
graph_maker.fill_between_y(ax=ax, xs=list(X_LIM), y0s=[CSC_THRESH] * 2,
                           y1s=[Y_LIM[1]] * 2, color='white', grad_end_color=2,
                           grad_hor=False, grad_log=True)

# Plot data:
for pos_i, ((x_loc, y_loc), cs) in enumerate(cscs.items()):
    graph_maker.violin(ax=ax, data=cs, color=0, position=pos_i + 1,
                       show_box=True, marker='dot', hist=False,
                       marker_color=1, median_color=1)

# Generate SVG:
graph_maker.write_svg()
