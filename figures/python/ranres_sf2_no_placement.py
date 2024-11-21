"""Generate the measured range and resolution for all RO designs for number
stages ranging from 1 to 4, without placement constraints figure for SmartFusion 2."""
import argparse
import sys
from typing import List, Tuple
import csv
from os import getcwd
from os.path import join
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position

DATA_FOLDER = join('measurements', 'no_placement_sf2')

RO_TYPES: List[str] = ['LUTVar0', 'LUTVar3', 'WireVar', 'GateVar']
YLIM = (5e-18, 1e-9)
STAGE_MARKERS: List[str] = ['circle', 'tri_down', 'square', 'diamond']
TEXT_OFSETS: List[Tuple[float, float]] = [(1e-2, -1.5e-12), (2e-3, 0),
                                          (1e-1, 2e-10), (0, -3e-11)]

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Store generated data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

if args.d:
    if args.v:
        print('Data argument not available')
    if args.q:
        sys.exit()

periods: List[List[Tuple[List[int], List[float]]]] = [[], [], [], []]

for stages in range(1, 5):
    periods[0].append(([], []))
    file_name = join(DATA_FOLDER, 'intralut0_np',
                     f'all_configs_intralut0_np_coso_x0y0_stages{stages}.csv')
    with open(file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            periods[0][-1][0].append(int(row[1]))
            periods[0][-1][1].append(float(row[2]) * 1e-9)
    periods[1].append(([], []))
    file_name = join(DATA_FOLDER, 'intralut3_np',
                     f'all_configs_intralut3_np_coso_x0y0_stages{stages}.csv')
    with open(file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            periods[1][-1][0].append(int(row[1]))
            periods[1][-1][1].append(float(row[2]) * 1e-9)
    periods[2].append(([], []))
    file_name = join(DATA_FOLDER, 'wireonly_np',
                     f'all_configs_wireonly_np_coso_x0y0_stages{stages}.csv')
    with open(file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            periods[2][-1][0].append(int(row[1]))
            periods[2][-1][1].append(float(row[2]) * 1e-9)
    periods[3].append(([], []))
    file_name = join(DATA_FOLDER, 'muxnetwork_np',
                     f'all_configs_muxnetwork_np_coso_x0y0_stages{stages}.csv')
    with open(file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            periods[3][-1][0].append(int(row[1]))
            periods[3][-1][1].append(float(row[2]) * 1e-9)

for ro_type, pers_ro_type in enumerate(periods):
    for nb_stages, (confs, pers) in enumerate(pers_ro_type):
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
        periods[ro_type][nb_stages] = (confs_tmp, pers_tmp)

ranges: List[List[float]] = []
for ro_type, pers_ro_type in enumerate(periods):
    ranges.append([])
    for nb_stages, (confs, pers) in enumerate(pers_ro_type):
        ranges[ro_type].append((np.quantile(pers, 0.75) # type: ignore
                                - np.quantile(pers, 0.25)) / np.median(pers)) # type: ignore

sorted_periods: List[List[List[float]]] = []
for ro_type, pers_ro_type in enumerate(periods):
    sorted_periods.append([])
    for _, pers in pers_ro_type:
        sorted_periods[ro_type].append(sorted(pers))

resolutions: List[List[float]] = []
for ro_type, pers_ro_type_sorted in enumerate(sorted_periods):
    resolutions.append([])
    for nb_stages_sorted, pers in enumerate(pers_ro_type_sorted):
        diffs: List[float] = [p1 - p0 for p0, p1 in zip(pers, pers[1:]) if p1 != p0]
        resolutions[ro_type].append(np.median(diffs)) # type: ignore

if args.v:
    print('Plotting sorted period lengths versus quantiles.')
    for pers_ro_type_sorted in sorted_periods:
        for pers_nb_stages_sorted in pers_ro_type_sorted:
            qs = [(i + 0.5) / len(pers_nb_stages_sorted) for i in range(len(pers_nb_stages_sorted))]
            plt.plot(qs, pers_nb_stages_sorted, 'o-') # type: ignore
        plt.show() # type: ignore

graph_maker = g_m.GraphMaker('ranres_sf2_no_placement.svg', figure_size=(1, 1),
                             folder_name='figures')
graph_maker.create_grid(size=(1, 1), marg_left=0.15)

ax = graph_maker.create_ax(0, 0, # pylint: disable=invalid-name
                           title=r'Range vs.\ resolution, no LP, no GP, SmartFusion 2',
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

if args.v:
    largest_res = max((max(r) for r in resolutions))
    smallest_res = min((min(r) for r in resolutions))
    if largest_res > YLIM[1]:
        print(f'YLIM too small: {largest_res} vs. {YLIM[1]}')
    if smallest_res < YLIM[0]:
        print(f'YLIM too large: {smallest_res} vs. {YLIM[0]}')

for ro_type, (res_ro_type, range_ro_type, name_ro_type, text_ofset) \
    in enumerate(zip(resolutions, ranges, RO_TYPES, TEXT_OFSETS)):
    graph_maker.plot(ax=ax, xs=range_ro_type, ys=res_ro_type,
                     color=ro_type)
    for xi, yi, stage_marker in zip(range_ro_type, res_ro_type, STAGE_MARKERS):
        graph_maker.plot(ax=ax, xs=[xi], ys=[yi], color=ro_type, marker=stage_marker)
    graph_maker.text(ax=ax, x=range_ro_type[0] + text_ofset[0],
                     y=res_ro_type[0] + text_ofset[1],
                     s=name_ro_type, color=ro_type)
for stage_marker, nb_stages in zip(STAGE_MARKERS, range(1, 5)):
    graph_maker.plot(ax=ax, xs=[], ys=[], marker=stage_marker, color='grey',
                     label=f'{nb_stages} stages' if nb_stages > 1 else '1 stage',
                     line_style='none')
graph_maker.write_svg()
