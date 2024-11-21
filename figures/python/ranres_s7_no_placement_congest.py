"""Generate the measured range and resolution for all RO designs for number
stages ranging from 1 to 4, on a congested FPGA, without placement constraints
figure for Spartan 7."""
import argparse
import sys
from typing import List, Tuple, Dict, Optional
import csv
import itertools as it
from os import getcwd
from os.path import join, isfile
import numpy as np
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import time_logger as tl # pylint: disable=wrong-import-position
from lib import store_data as sd # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'no_placement_s7')
DATA_FOLDER_CON = join('measurements', 'no_placement_congestion_s7')

RO_TYPES: List[str] = ['intralut0', 'intralut5', 'wireonly', 'muxnetwork']
RO_NAMES: List[str] = ['LUTVar0', 'LUTVar5', 'WireVar', 'GateVar']
YLIM = (5e-18, 1e-9)
STAGE_MARKERS: List[str] = ['circle', 'tri_down', 'square', 'diamond']
TEXT_OFSETS: List[Tuple[float, float]] = [(1e-2, -7.5e-13), (4e-4, -4e-15),
                                          (1e-1, -8.1e-11), (-3e-2, -3e-11)]
STAGES: List[int] = list(range(1, 5))

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-l', help='Time-log process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

store_data = sd.StoreData(name='ranres_s7_no_placement_congest')

resolutions: Dict[str, Dict[int, float]] = {}
ranges: Dict[str, Dict[int, float]] = {}
resolutions_con: Dict[str, float] = {}
ranges_con: Dict[str, float] = {}

if args.d:
    periods: Dict[str, Dict[int, Tuple[List[int], List[float]]]] = {}
    periods_con: Dict[str, Tuple[List[int], List[float]]] = {}

    # Read files:
    for ro_type, stages in it.product(RO_TYPES, STAGES):
        if ro_type not in periods:
            periods[ro_type] = {}
        file_name = join(DATA_FOLDER, ro_type + '_np',
                         f'all_configs_{ro_type}_np_coso_x0y0_stages{stages}.csv')
        if not isfile(file_name):
            if args.v:
                print(f'File: {file_name} does not exist!')
            continue
        pers_read: Tuple[List[int], List[float]] = ([], [])
        with open(file_name, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                pers_read[0].append(int(row[1]))
                pers_read[1].append(float(row[2]) * 1e-9)
        if not pers_read[0]:
            if args.v:
                print(f'File: {file_name} is empty!')
            continue
        periods[ro_type][stages] = pers_read
    for ro_type in RO_TYPES:
        confs: List[int] = []
        pers: List[float] = []
        file_name = join(DATA_FOLDER_CON, ro_type + '_np_cg',
                         f'all_configs_{ro_type}_np_congest_coso_x0y0_stages4.csv')
        with open(file_name, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                confs.append(int(row[1]))
                pers.append(float(row[2]) * 1e-9)
        periods_con[ro_type] = (confs, pers)

    # Average over identical confs:
    logger = tl.TimeLogger(len(RO_TYPES) * len(STAGES))
    if args.v & args.l:
        logger.start()
    for ro_type, stages in it.product(RO_TYPES, STAGES):
        if stages not in periods[ro_type]:
            if args.v & args.l:
                logger.iterate()
            continue
        confs, pers = periods[ro_type][stages]
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
        periods[ro_type][stages] = (confs_tmp, pers_tmp)
        if args.v & args.l:
            logger.iterate()
    if args.v & args.l:
        logger.clear()
    for ro_type, (confs, pers) in periods_con.items():
        confs_tmp = []
        pers_tmp = []
        nbs_tmp = []
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
        periods_con[ro_type] = (confs_tmp, pers_tmp)

    # Calculate ranges:
    for ro_type, stages in it.product(RO_TYPES, STAGES):
        if stages not in periods[ro_type]:
            continue
        if ro_type not in ranges:
            ranges[ro_type] = {}
        _, pers = periods[ro_type][stages]
        ran: float = (np.quantile(pers, 0.75) # type: ignore
                      - np.quantile(pers, 0.25)) / np.median(pers) # type: ignore
        ranges[ro_type][stages] = ran
    for ro_type, (_, pers) in periods_con.items():
        ranges_con[ro_type] = (np.quantile(pers, 0.75) # type: ignore
                               - np.quantile(pers, 0.25)) / np.median(pers) # type: ignore

    # Generate sorted periods:
    sorted_periods: Dict[str, Dict[int, List[float]]] = {}
    sorted_periods_con: Dict[str, List[float]] = {}
    for ro_type, stages in it.product(RO_TYPES, STAGES):
        if stages not in periods[ro_type]:
            continue
        if ro_type not in sorted_periods:
            sorted_periods[ro_type] = {}
        _, pers = periods[ro_type][stages]
        sorted_periods[ro_type][stages] = sorted(pers)
    for ro_type, (_, pers) in periods_con.items():
        sorted_periods_con[ro_type] = sorted(pers)

    # Calculate resolutions:
    for ro_type, stages in it.product(RO_TYPES, STAGES):
        if stages not in periods[ro_type]:
            continue
        if ro_type not in resolutions:
            resolutions[ro_type] = {}
        pers = sorted_periods[ro_type][stages]
        diffs: List[float] = [p1 - p0 for p0, p1 in zip(pers, pers[1:]) if p1 != p0]
        resolutions[ro_type][stages] = np.median(diffs) # type: ignore
    for ro_type, sorted_pers in sorted_periods_con.items():
        diffs = [p1 - p0 for p0, p1 in zip(sorted_pers, sorted_pers[1:]) if p1 != p0]
        resolutions_con[ro_type] = np.median(diffs) # type: ignore

    # Print out stats:
    if args.v:
        for ro_type, ro_name in zip(RO_TYPES, RO_NAMES):
            print(f'{ro_name}, period mean: {np.mean(periods_con[ro_type][1]) * 1e9}, '
                f'freq mean: {np.mean([1/x for x in periods_con[ro_type][1]]) / 1e6}, '
                f'period median: {np.median(periods_con[ro_type][1]) * 1e9}, '
                f'period std: {np.std(periods_con[ro_type][1]) * 1e9}')

    # Store calculated data:
    data: Optional[List[List[float]]] = []
    assert data is not None
    for (ro_index, ro_type), stages in it.product(enumerate(RO_TYPES), STAGES):
        if stages not in periods[ro_type]:
            continue
        res = resolutions[ro_type][stages]
        ran = ranges[ro_type][stages]
        data.append([ro_index, stages, res, ran])
    for ro_type in periods_con:
        ro_index = RO_TYPES.index(ro_type)
        res = resolutions_con[ro_type]
        ran = ranges_con[ro_type]
        data.append([ro_index, -1, res, ran])
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
    for ro_index_f, stages_f, res, ran in data:
        ro_type = RO_TYPES[int(ro_index_f)]
        if stages_f < 0:
            ranges_con[ro_type] = ran
            resolutions_con[ro_type] = res
        else:
            if ro_type not in ranges:
                ranges[ro_type] = {}
                resolutions[ro_type] = {}
            ranges[ro_type][int(stages_f)] = ran
            resolutions[ro_type][int(stages_f)] = res

graph_maker = g_m.GraphMaker('ranres_s7_no_placement_congest.svg', figure_size=(1, 1),
                             folder_name='figures')
graph_maker.create_grid(size=(1, 1), marg_left=0.15)

ax = graph_maker.create_ax(0, 0, # pylint: disable=invalid-name
                           title=r'Range vs.\ resolution, congested, Spartan 7',
                           x_label='Normalized range',
                           y_label='Resolution',
                           x_unit='-',
                           y_unit='s',
                           x_scale='log10',
                           y_scale='log10',
                           show_legend=True,
                           y_invert=True,
                           y_lim=YLIM,
                           legend_loc='lower left',
                           x_grid=True, y_grid=True)

# Check y range:
if args.v:
    largest_res = max((r1 for r0 in resolutions.values() for r1 in r0.values()))
    smallest_res = min((r1 for r0 in resolutions.values() for r1 in r0.values()))
    largest_res_con = max(resolutions_con.values())
    smallest_res_con = min(resolutions_con.values())
    if largest_res > YLIM[1]:
        print(f'YLIM too small: {largest_res} vs. {YLIM[1]}')
    if smallest_res < YLIM[0]:
        print(f'YLIM too large: {smallest_res} vs. {YLIM[0]}')

# Plot points:
for color, (ro_type, ro_name, (x_off, y_off)) in enumerate(zip(RO_TYPES, RO_NAMES, TEXT_OFSETS)):
    rans: List[float] = []
    ress: List[float] = []
    for stages, marker in zip(STAGES, STAGE_MARKERS):
        if stages not in ranges[ro_type]:
            continue
        ran = ranges[ro_type][stages]
        res = resolutions[ro_type][stages]
        rans.append(ran)
        ress.append(res)
    graph_maker.plot(ax=ax, xs=rans, ys=ress, color=color, line_style='dashed',
                     alpha=0.5, edge_alpha=0.5, marker_color=color, marker_edge_color=color)
    graph_maker.text(ax=ax, x=rans[0] + x_off,
                     y=ress[0] + y_off,
                     s=ro_name, color=color)
for color, (ro_type, ro_name, (x_off, y_off)) in enumerate(zip(RO_TYPES, RO_NAMES, TEXT_OFSETS)):
    if ro_type not in ranges_con:
        continue
    ran = ranges_con[ro_type]
    res = resolutions_con[ro_type]
    graph_maker.plot(ax=ax, xs=[ran], ys=[res],
                     color=color, marker=STAGE_MARKERS[3],
                     marker_color=color)

# Construct legend entries:
for color, ro_name in enumerate(RO_NAMES):
    graph_maker.plot(ax=ax, xs=[], ys=[], color=color,
                     line_style='dashed', alpha=0.5,
                     label=ro_name)
graph_maker.plot(ax=ax, xs=[], ys=[], color='grey', line_style='none',
                 marker=STAGE_MARKERS[3], label='Congested')

# Generate SVG:
graph_maker.write_svg()
