"""Generate obtainable C values with fixed placement on Spartan 7 figure."""
import argparse
import sys
import csv
import itertools as it
from os import getcwd
from os.path import join, isfile
from typing import List, Dict
from pylfsr import LFSR # type: ignore # pylint: disable=import-error
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'lp_variable_gp_s7')

RO_NAMES: List[str] = ['GateVar', 'WireVar', 'LUTVar0', 'LUTVar5']
RO_TYPES: List[str] = ['muxnetwork', 'wireonly', 'intralut0', 'intralut5']

X_LOC_0: int = 0
Y_LOC_0: int = 0
X_LOC_1: int = 0
Y_LOC_1: int = 74
STAGES: int = 4

MAX_NB_CSC: int = 2**16

CSC_THRESH = 59.0

X_LIM = (0.5, 4.5)
Y_LIM = (0.8, 1e4)

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = s_d.StoreData(name='csc_s7_fixed_placement')

cscs: Dict[str, List[float]] = {}
if args.d:
    def bi2nu(bi: List[int]) -> int:
        """Binary to decimal."""
        result: int = 0
        for i_, b in enumerate(bi):
            result += b * 2**(i_)
        return result

    # Parse CSV files:
    for ro_type in RO_TYPES:
        file_name_0 = join(DATA_FOLDER, (f'{ro_type}/all_configs_{ro_type}'
                                         f'_x{X_LOC_0}y{Y_LOC_0}_stages{STAGES}.csv'))
        file_name_1 = join(DATA_FOLDER, (f'{ro_type}/all_configs_{ro_type}'
                                         f'_x{X_LOC_1}y{Y_LOC_1}_stages{STAGES}.csv'))
        if not isfile(file_name_0):
            if args.v:
                print(f'File: {file_name_0} does not exist!')
            continue
        if not isfile(file_name_1):
            if args.v:
                print(f'File: {file_name_1} does not exist!')
            continue
        d_0s: List[float] = []
        d_1s: List[float] = []
        with open(file_name_0, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                d_0s.append(float(row[1]))
        if not d_0s:
            if args.v:
                print(f'File: {file_name_0} is empty!')
            continue
        with open(file_name_1, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                d_1s.append(float(row[1]))
        if not d_1s:
            if args.v:
                print(f'File: {file_name_1} is empty!')
            continue
        cscs_read: List[float] = []
        if len(d_0s) * len(d_1s) > MAX_NB_CSC:
            nb_db_0 = int(np.log2(len(d_0s)))
            nb_db_1 = int(np.log2(len(d_1s)))
            if (nb_db_0 + nb_db_1 != 40) & (nb_db_0 + nb_db_1 != 30):
                if args.v:
                    print(f'{ro_type}, # bits is not 40 or 30: {nb_db_0 + nb_db_1}')
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
                print(f'{ro_type}: CSCs is empty!')
            continue
        if args.v:
            print(f'{ro_type}: # RO0: {len(d_0s)}, # RO1: {len(d_1s)}, '
                  f'# CSC: {len(cscs_read)}, '
                  f'# dropped: {len(d_0s) * len(d_1s) - len(cscs_read)}')
        cscs[ro_type] = cscs_read

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

graph_maker = g_m.GraphMaker('csc_s7_fixed_placement.svg', figure_size=(1, 1),
                             folder_name='figures', figure_height_scale=0.75)
graph_maker.create_grid(size=(1, 1), marg_top=0.85, marg_bot=0.2)

ax = graph_maker.create_ax(x_slice=0, y_slice=0, # pylint: disable=invalid-name
                           title='Obtainable $C$ values with placement',
                           x_label='RO topology', y_label='$C$',
                           x_unit='-', y_unit='-',
                           y_scale='log10', x_scale='fix',
                           y_grid=True,
                           fixed_locs_x=[1, 2, 3, 4],
                           fixed_labels_x=RO_NAMES)

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
