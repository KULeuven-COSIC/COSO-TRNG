"""Plot the ranres point cloud for all 25 locations, for 1-4 number of stages."""
import argparse
import sys
from typing import List, Tuple, Dict, Optional
import csv
from os import getcwd
from os.path import join
import itertools as it
import os.path
import numpy as np
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position
from lib import time_logger as t_l # pylint: disable=wrong-import-position

RO_NAMES: List[str] = ['LUTVar0', 'LUTVar5', 'WireVar', 'GateVar']
RO_TYPES: List[str] = ['intralut0', 'intralut5', 'wireonly', 'muxnetwork']
YLIM = (5e-18, 1e-9)
STAGE_MARKERS: List[str] = ['circle', 'tri_down', 'square', 'diamond']
TEXT_OFSETS: List[Tuple[float, float]] = [(0, 3e-14), (0, 0),
                                          (0, 2e-13), (-1e-1, 2e-12)]
X_LOCS: List[int] = [0, 10, 28, 36, 52]
Y_LOCS: List[int] = [0, 37, 74, 111, 148]
STAGES: List[int] = list(range(1, 5))

DATA_FOLDER = join('measurements', 'lp_variable_gp_s7')

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-l', help='Time-log process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = s_d.StoreData(name='ranres_s7_variable_gp')

resolutions: Dict[str, Dict[int, Dict[Tuple[int, int], float]]] = {}
ranges: Dict[str, Dict[int, Dict[Tuple[int, int], float]]] = {}

if args.d:
    periods: Dict[str, Dict[int, Dict[Tuple[int, int], Tuple[List[int], List[float]]]]] = {}

    # Parse CSV files:
    for ro_type, stages, x_loc, y_loc in it.product(RO_TYPES, STAGES, X_LOCS, Y_LOCS):
        if ro_type not in periods:
            periods[ro_type] = {}
        if stages not in periods[ro_type]:
            periods[ro_type][stages] = {}
        file_name = join(DATA_FOLDER, ro_type,
                         f'all_configs_{ro_type}_x{x_loc}y{y_loc}_'
                         f'stages{stages}.csv')
        if not os.path.isfile(file_name):
            if args.v:
                print(f'File: {file_name} does not exist!')
            continue
        pers_read: Tuple[List[int], List[float]] = ([], [])
        with open(file_name, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                pers_read[0].append(int(row[0]))
                pers_read[1].append(float(row[1]) * 1e-9)
        if not pers_read[0]:
            if args.v:
                print(f'File: {file_name} is empty!')
            continue
        periods[ro_type][stages][(x_loc, y_loc)] = pers_read

    # Average over identical confs:
    logger = t_l.TimeLogger(len(RO_TYPES) * len(STAGES) * len(X_LOCS) * len(Y_LOCS))
    if args.v & args.l:
        logger.start()
    for ro_type, stages, x_loc, y_loc in it.product(RO_TYPES, STAGES, X_LOCS, Y_LOCS):
        if (x_loc, y_loc) not in periods[ro_type][stages]:
            continue
        confs, pers = periods[ro_type][stages][(x_loc, y_loc)]
        confs_tmp: List[int] = []
        pers_tmp: List[float] = []
        nbs_tmp: List[int] = []
        for conf, per in zip(confs, pers):
            if conf in confs_tmp:
                conf_index = confs_tmp.index(conf)
                pers_tmp[conf_index] = (pers_tmp[conf_index] * nbs_tmp[conf_index] + per) \
                    / (nbs_tmp[conf_index] + 1)
                nbs_tmp[conf_index] += 1
            else:
                confs_tmp.append(conf)
                pers_tmp.append(per)
                nbs_tmp.append(1)
        periods[ro_type][stages][(x_loc, y_loc)] = (confs_tmp, pers_tmp)
        if args.v & args.l:
            logger.iterate()
    if args.v & args.l:
        logger.clear()

    # Calculate ranges:
    for ro_type, stages, x_loc, y_loc in it.product(RO_TYPES, STAGES, X_LOCS, Y_LOCS):
        if (x_loc, y_loc) not in periods[ro_type][stages]:
            continue
        if ro_type not in ranges:
            ranges[ro_type] = {}
        if stages not in ranges[ro_type]:
            ranges[ro_type][stages] = {}
        _, pers = periods[ro_type][stages][(x_loc, y_loc)]
        ran: float = (np.quantile(pers, 0.75) # type: ignore
                      - np.quantile(pers, 0.25)) / np.median(pers) # type: ignore
        ranges[ro_type][stages][(x_loc, y_loc)] = ran

    # Generate sorted periods:
    sorted_periods: Dict[str, Dict[int, Dict[Tuple[int, int], List[float]]]] = {}
    for ro_type, stages, x_loc, y_loc in it.product(RO_TYPES, STAGES, X_LOCS, Y_LOCS):
        if (x_loc, y_loc) not in periods[ro_type][stages]:
            continue
        if ro_type not in sorted_periods:
            sorted_periods[ro_type] = {}
        if stages not in sorted_periods[ro_type]:
            sorted_periods[ro_type][stages] = {}
        _, pers = periods[ro_type][stages][(x_loc, y_loc)]
        sorted_periods[ro_type][stages][(x_loc, y_loc)] = sorted(pers)

    # Calculate resolutions:
    for ro_type, stages, x_loc, y_loc in it.product(RO_TYPES, STAGES, X_LOCS, Y_LOCS):
        if (x_loc, y_loc) not in periods[ro_type][stages]:
            continue
        if ro_type not in resolutions:
            resolutions[ro_type] = {}
        if stages not in resolutions[ro_type]:
            resolutions[ro_type][stages] = {}
        pers = sorted_periods[ro_type][stages][(x_loc, y_loc)]
        diffs: List[float] = [p1 - p0 for p0, p1 in zip(pers, pers[1:]) if p1 != p0]
        resolutions[ro_type][stages][(x_loc, y_loc)] = np.median(diffs) # type: ignore

    # Print out stats:
    if args.v:
        for ro_type, ro_name in zip(RO_TYPES, RO_NAMES):
            print(f'{ro_name}, period mean: {np.mean(periods[ro_type][4][(0, 0)][1]) * 1e9}, '
                f'freq mean: {np.mean([1/x for x in periods[ro_type][4][(0, 0)][1]]) / 1e6}, '
                f'period median: {np.median(periods[ro_type][4][(0, 0)][1]) * 1e9}, '
                f'period std: {np.std(periods[ro_type][4][(0, 0)][1]) * 1e9}')

    # Store calculated data:
    data: Optional[List[List[float]]] = []
    for (ro_index, ro_type), stages, x_loc, y_loc \
        in it.product(enumerate(RO_TYPES), STAGES, X_LOCS, Y_LOCS):
        if (x_loc, y_loc) not in periods[ro_type][stages]:
            continue
        res = resolutions[ro_type][stages][(x_loc, y_loc)]
        ran = ranges[ro_type][stages][(x_loc, y_loc)]
        data.append([ro_index, stages, x_loc, y_loc, res, ran])
    store_data.write_data(data, True)
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
    for ro_index, stages, x_loc, y_loc, res, ran in data:
        ro_type = RO_TYPES[int(ro_index)]
        if ro_type not in ranges:
            ranges[ro_type] = {}
            resolutions[ro_type] = {}
        if int(stages) not in ranges[ro_type]:
            ranges[ro_type][int(stages)] = {}
            resolutions[ro_type][int(stages)] = {}
        ranges[ro_type][int(stages)][(int(x_loc), int(y_loc))] = ran
        resolutions[ro_type][int(stages)][(int(x_loc), int(y_loc))] = res

graph_maker = g_m.GraphMaker('ranres_s7_variable_gp.svg', figure_size=(1, 1),
                             folder_name='figures')
graph_maker.create_grid(size=(1, 1), marg_left=0.15)

ax = graph_maker.create_ax(0, 0, # pylint: disable=invalid-name
                           title=r'Range vs.\ resolution, variable GP, Spartan 7',
                           x_label='Normalized range',
                           y_label='Resolution',
                           x_unit='-',
                           y_unit='s',
                           x_scale='log10',
                           y_scale='log10',
                           show_legend=True,
                           y_invert=True,
                           y_lim=YLIM,
                           legend_loc='upper right',
                           x_grid=True, y_grid=True)

# Check y range:
if args.v:
    largest_res = max((r2 for r0 in resolutions.values() for r1 in r0.values()
                       for r2 in r1.values()))
    smallest_res = min((r2 for r0 in resolutions.values() for r1 in r0.values()
                        for r2 in r1.values()))
    if largest_res > YLIM[1]:
        print(f'YLIM too small: {largest_res} vs. {YLIM[1]}')
    if smallest_res < YLIM[0]:
        print(f'YLIM too large: {smallest_res} vs. {YLIM[0]}')

# Plot points:
for color, (ro_type, ro_name, (x_off, y_off)) in enumerate(zip(RO_TYPES, RO_NAMES, TEXT_OFSETS)):
    mean_ran: float = 0
    mean_res: float = 0
    nb_points: int = 0
    for (stages, marker), x_loc, y_loc in it.product(zip(STAGES, STAGE_MARKERS), X_LOCS, Y_LOCS):
        if (x_loc, y_loc) not in ranges[ro_type][stages]:
            continue
        ran = ranges[ro_type][stages][(x_loc, y_loc)]
        res = resolutions[ro_type][stages][(x_loc, y_loc)]
        graph_maker.plot(ax=ax, xs=[ran], ys=[res],
                        color=color, marker=marker, alpha=0.3, line_width=0.8,
                        marker_color=color, marker_edge_color='none')
        mean_ran += np.log(ran)
        mean_res += np.log(res)
        nb_points += 1
    mean_ran = np.exp(mean_ran / nb_points)
    mean_res = np.exp(mean_res / nb_points)
    graph_maker.text(ax=ax, x=mean_ran + x_off, y=mean_res / 100 + y_off, s=ro_name, color=color)

# Construct legend entries:
for stage_marker, nb_stages in zip(STAGE_MARKERS, STAGES):
    graph_maker.plot(ax=ax, xs=[], ys=[], marker=stage_marker, color='grey',
                     label=f'{nb_stages} stages' if nb_stages > 1 else '1 stage',
                     line_style='none')

# Generate SVG:
graph_maker.write_svg()
