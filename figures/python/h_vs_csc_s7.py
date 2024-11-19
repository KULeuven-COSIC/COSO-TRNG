"""Generate estimated min-entropy and HTP versus delta and C figure for Spartan 7."""
import argparse
import sys
import csv
from os import getcwd
from os.path import join
from typing import List
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(getcwd())
from lib import graph_maker as g_m # pylint: disable=wrong-import-position
from lib import store_data as s_d # pylint: disable=wrong-import-position

JIT_STRENGTH = 4.6e-15
RO_PER = 3.69e-9

CSC_MM = (0, 200)
H_MM = (-0.05, 1.05)
NB_SAMPLES = CSC_MM[1] - CSC_MM[0]

EXP_FOLDER = 'math_model/results/'
RAW_DATA_FOLDER = EXP_FOLDER

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='Print process', action='store_true')
parser.add_argument('-d', help='Collect data', action='store_true')
parser.add_argument('-q', help='Quit after data collect', action='store_true')
args = parser.parse_args()

hs: List[float] = []
cscs: List[float] = []
htps: List[float] = []
ds: List[float] = []

store_data = s_d.StoreData(name='h_vs_csc_s7')

if args.d:
    file_name = f'csc_jit{int(JIT_STRENGTH * 1e16)}_per{int(RO_PER * 1e11)}.csv'
    with open(join(RAW_DATA_FOLDER, file_name), 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            hs.append(float(row[1]))
            cscs.append(float(row[0]))
            htps.append(float(row[1]) / (float(row[0]) * RO_PER))
            ds.append(RO_PER / float(row[0]))

    data_to_write = [cscs, ds, hs, htps]
    store_data.write_data(data_to_write, over_write=True)
    if args.q:
        sys.exit()
else:
    if not store_data.file_exist:
        if args.v:
            print(f'File: {store_data.file_path} does not exist!')
        sys.exit()
    data = store_data.read_data()
    if data is None:
        if args.v:
            print(f'Error in data: {store_data.file_path}!')
            sys.exit()
    assert data is not None
    cscs, ds, hs, htps = tuple(data)

if args.v:
    plt.plot(cscs, hs) # type: ignore
    plt.show() # type: ignore
    plt.plot(cscs, htps) # type: ignore
    plt.show() # type: ignore

graph_maker = g_m.GraphMaker('h_vs_csc_s7.svg', figure_size=(1, 1), folder_name='figures')
graph_maker.create_grid(size=(3, 1), y_ratios=[1, 0, 1],
                        marg_mid_hor=0, marg_mid_ver=0, marg_top=0.77, marg_left=0.11,
                        marg_bot=0.16)

# Determine Delta locs:
delta_nbs: List[float] = [np.inf, 200e-12, 100e-12, 75e-12, 50e-12, 35e-12, 25e-12, 20e-12]
delta_locs: List[float] = [RO_PER / d for d in delta_nbs]
delta_labels: List[str] = [str(int(d * 1e12)) if d != np.inf else r'$\infty$' for d in delta_nbs]

# Determine max HTP:
HTP_MM = (min(htps) * 0.9, max(htps) * 1.1)

# Determine 0.91 min-entropy point:
index_91 = len(cscs) - 1
while hs[index_91] >= 0.91:
    index_91 -= 1
csc_91 = cscs[index_91 + 1]
d_91 = ds[index_91 + 1]
htp_91 = htps[index_91 + 1]
h_91 = hs[index_91 + 1]
if args.v:
    print(f'0.91 min-entropy point: C={csc_91}, D={d_91}, HTP={htp_91}, H={h_91}')

# Create axes:
ax_h = graph_maker.create_ax(x_slice=0, y_slice=0, # pylint: disable=invalid-name
                             x_scale='lin', y_scale='lin',
                             x_label=r'Counter output ($\mathbf{E}[C]$)',
                             x_unit='-',
                             y_label='Min-entropy',
                             y_unit='bit',
                             title=(r'Min-entropy and HTP versus '
                                    r'$\mathbf{E}[\Delta]$ and $\mathbf{E}[C]$'),
                             y_grid=True, x_grid=True,
                            #  show_legend=True,
                             x_label_bot=False, x_label_top=True,
                             x_lim=CSC_MM,
                             y_lim=H_MM)
ax_htp = graph_maker.create_ax(x_slice=0, y_slice=2, # pylint: disable=invalid-name
                               x_scale='fix', y_scale='lin',
                               x_label=r'Period length difference ($\mathbf{E}[\Delta]$)',
                               x_unit='ps',
                               y_label='HTP',
                               y_unit='bit/s',
                               y_grid=True, x_grid=True,
                               fixed_locs_x=delta_locs,
                               fixed_labels_x=delta_labels,
                               x_lim=CSC_MM, y_lim=HTP_MM)

# Fill green:
graph_maker.fill_between_y(ax=ax_h, xs=list(CSC_MM), y0s=[H_MM[1]] * 2,
                           y1s=[h_91] * 2, color='green')
graph_maker.fill_between_y(ax=ax_htp, xs=[csc_91, CSC_MM[1]], y0s=[HTP_MM[0]] * 2,
                           y1s=[HTP_MM[1]] * 2, color=2, grad_end_color='white')

# Plot data:
graph_maker.plot(ax=ax_h, xs=cscs, ys=hs, color=0)
graph_maker.plot(ax=ax_htp, xs=cscs, ys=htps, color=0)

# Plot entropy 0.91 point:
graph_maker.plot(ax=ax_h, xs=[csc_91], ys=[h_91], line_style='none', color=1,
                 marker='cross', marker_color=1, marker_edge_color=1)
graph_maker.plot(ax=ax_htp, xs=[csc_91], ys=[htp_91], line_style='none', color=1,
                 marker='cross', marker_color=1, marker_edge_color=1)
graph_maker.text(ax=ax_h, x=csc_91, y=h_91, s=(r'$\mathbf{E}[C]$ = ' f'{csc_91:2.0f}'),
                 color=1, border_color='white', hor_align='left', ver_align='top',
                 y_delta=-6)
graph_maker.text(ax=ax_h, x=csc_91, y=h_91, s=(r'$\mathbf{E}[\Delta]$ = '
                                               f'{d_91 * 1e12:4.1f} ps'),
                 color=1, border_color='white', hor_align='left', ver_align='top',
                 y_delta=-18)
graph_maker.text(ax=ax_htp, x=csc_91, y=htp_91, s=(r'HTP = '
                                                   f'{htp_91 / 1e6:3.1f} Mbit/s'),
                 color=1, border_color='white', ver_align='top',
                 y_delta=-20)

# Generate SVG:
graph_maker.write_svg()
