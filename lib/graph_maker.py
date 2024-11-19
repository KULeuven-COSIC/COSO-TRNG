"""A module using the pyplot module for creating graphs.""" # pylint: disable=too-many-lines
from typing import Optional, Tuple, List, cast, Any, Dict, Union
import json
import os
from enum import Enum
from matplotlib import __version__ as MPL_VERSION # type: ignore # pylint: disable=no-name-in-module
import matplotlib.pyplot as plt # type: ignore
import matplotlib.gridspec as grid # type: ignore
import matplotlib.spines as spi # type: ignore
import matplotlib.ticker as tic # type: ignore
import matplotlib.scale as sca # type: ignore
import matplotlib.colors as mco # type: ignore
import matplotlib.axes as mla # type: ignore
import matplotlib.lines as mli # type: ignore
import matplotlib.axis as mxs # type: ignore
import matplotlib.transforms as mtr # type: ignore
import matplotlib.patheffects as mpe # type: ignore
import matplotlib.markers as mma # type: ignore
import matplotlib._enums as men # type: ignore
import cycler # type: ignore
import numpy as np

class GraphMaker:
    """A class containing graph making functionality."""

    _default_param_file: str = 'lib/graph_params.json'
    si_prefixes: List[str] = ['q', 'r', 'y', 'z', 'a', 'f', 'p', 'n', r'$\mu$', 'm', '',
                              'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R', 'Q']

    def __init__(self, file_name: str, param_file: Optional[str]=None,
                 figure_size: Tuple[int, int]=(1, 1), folder_name: str='',
                 figure_height_scale: float=1):
        self._file_name = file_name
        self._folder_name = folder_name
        self._figure_size = figure_size
        if param_file is None:
            param_file = GraphMaker._default_param_file
        self._param_file = param_file
        with open(self._param_file, 'r', encoding='utf-8') as f:
            self._graph_params = json.loads(f.read())
        self._fig_dpi = cast(float, plt.rcParams['figure.dpi'])
        fig_width_inch = int(cast(int, self._graph_params['global']['svg_width']) \
                             / self._fig_dpi) * self._figure_size[0]
        fig_height_inch = int(cast(int, self._graph_params['global']['svg_height']) \
                              / self._fig_dpi) * self._figure_size[1] * figure_height_scale
        self._fig = plt.figure(figsize=(fig_width_inch, fig_height_inch)) # type: ignore
        self._grid: Optional['grid.GridSpec'] = None
        self._axes: List['plt.Axes'] = []
        self._ax_data: List[Tuple[str, str, Optional[str], Optional[str],
                                  str, str, bool, str, List[mli.Line2D], List[float],
                                  Optional[List[float]], Optional[int],
                                  float, Optional[float], Optional[float]]] = []
        gp_graph_colors: List[str] = self._graph_params['data']['cols']
        custom_color_cyc = cycler.cycler(color=gp_graph_colors) # type: ignore
        plt.rcParams['axes.prop_cycle'] = custom_color_cyc
        plt.rcParams['text.latex.preamble'] = r'''
        \usepackage[T1]{fontenc}
        \usepackage{DejaVuSansMono}
        \renewcommand{\familydefault}{\ttdefault}
        \usepackage[utf8]{inputenc}
        \usepackage[euler]{textgreek}
        \usepackage{siunitx}
        \usepackage{amsmath}
        \usepackage{amsfonts}
        \DeclareSymbolFont{lettersA}{U}{txmia}{m}{it}
        \SetSymbolFont{lettersA}{bold}{U}{txmia}{bx}{it}
        \DeclareFontSubstitution{U}{txmia}{m}{it}
        \DeclareMathSymbol{\piup}{\mathord}{lettersA}{25}
        \DeclareMathSymbol{\gammaup}{\mathord}{lettersA}{13}
        '''
        plt.rcParams['font.family'] = 'monospace'
        plt.rcParams['font.monospace'] = ['DejaVu Sans Mono']
        plt.rcParams['text.usetex'] = True
        # gp_font_family: str = self._graph_params['label']['font_name']
        # plt.rcParams['mathtext.fontset'] = 'custom'
        # plt.rcParams['mathtext.rm'] = gp_font_family
        # plt.rcParams['mathtext.it'] = gp_font_family + ':italic'
        # plt.rcParams['mathtext.bf'] = gp_font_family + ':bold'

    def create_grid(self, size: Tuple[int, int]=(1, 1),
                    x_ratios: Optional[List[float]]=None,
                    y_ratios: Optional[List[float]]=None,
                    marg_mid_hor: Optional[float]=None,
                    marg_mid_ver: Optional[float]=None,
                    marg_bot: Optional[float]=None,
                    marg_top: Optional[float]=None,
                    marg_right: Optional[float]=None,
                    marg_left: Optional[float]=None) \
        -> None:
        """Create a figure grid."""
        if x_ratios is None:
            x_ratios = [1.0] * size[1]
        if y_ratios is None:
            y_ratios = [1.0] * size[0]
        if marg_mid_hor is None:
            marg_mid_hor = self._graph_params['axes']['marg_mid_hor']
        if marg_mid_ver is None:
            marg_mid_ver = self._graph_params['axes']['marg_mid_ver']
        if marg_bot is None:
            marg_bot = self._graph_params['axes']['marg_bot']
        if marg_top is None:
            marg_top = self._graph_params['axes']['marg_top']
        if marg_right is None:
            marg_right = self._graph_params['axes']['marg_right']
        if marg_left is None:
            marg_left = self._graph_params['axes']['marg_left']
        self._grid = grid.GridSpec(*size, width_ratios=x_ratios, height_ratios=y_ratios,
                                   wspace=marg_mid_hor, hspace=marg_mid_ver, # type: ignore
                                   bottom=marg_bot, top=marg_top, # type: ignore
                                   right=marg_right, left=marg_left) # type: ignore

    def create_ax(self, x_slice: Union[slice, int]=slice(None),
                  y_slice: Union[slice, int]=slice(None),
                  title: Optional[str]=None, title_pad: Optional[float]=None,
                  title_loc: Optional[str]=None,
                  x_label: Optional[str]=None, y_label: Optional[str]=None,
                  x_unit: str='-', y_unit: str='-',
                  x_scale: str='lin', y_scale: str='lin',
                  show_x_ticks: bool=True, show_y_ticks: bool=True,
                  show_x_labels: bool=True, show_y_labels: bool=True,
                  max_nb_x_ticks: Optional[int]=None, max_nb_y_ticks: Optional[int]=None,
                  x_grid: bool=False, y_grid: bool=False,
                  share_x: Optional[int]=None, share_y: Optional[int]=None,
                  show_legend: bool=False, legend_loc: str='best',
                  legend_bbox: Optional[List[float]]=None,
                  x_invert: bool=False, y_invert: bool=False,
                  x_lim: Optional[Tuple[float, float]]=None,
                  y_lim: Optional[Tuple[float, float]]=None,
                  hide_x_ticks: bool=False, hide_y_ticks: bool=False,
                  fixed_locs_x: Optional[List[float]]=None,
                  fixed_locs_y: Optional[List[float]]=None,
                  fixed_labels_x: Optional[List[str]]=None,
                  fixed_labels_y: Optional[List[str]]=None,
                  nb_leg_cols: Optional[int]=None,
                  leg_font_size: float=1,
                  x_label_bot: bool=True,
                  x_label_top: bool=False,
                  y_label_left: bool=True,
                  y_label_right: bool=False,
                  x_label_pad: Optional[float]=None,
                  y_label_pad: Optional[float]=None,
                  x_label_rotate: Optional[float]=None,
                  y_label_rotate: Optional[float]=None,
                  x_spines: str='both',
                  y_spines: str='both',
                  x_spine_center: bool=False,
                  y_spine_center: bool=False,
                  x_arrow: bool=False,
                  y_arrow: bool=False,
                  leg_handle_len: Optional[float]=None,
                  leg_column_space: Optional[float]=None,
                  label_font_size: Optional[float]=None,
                  x_label_precision: int=1,
                  y_label_precision: int=1,
                  x_label_color: Optional[Union[int, str]]=None,
                  y_label_color: Optional[Union[int, str]]=None) -> int:
        """Create a new axis with the given postion slices."""
        if self._grid is None:
            return -1
        subplot_kwargs: Dict[str, Any] = {}
        # Share the axis with another subplot:
        if share_x is not None:
            subplot_kwargs['sharex'] = self._axes[share_x]
        if share_y is not None:
            subplot_kwargs['sharey'] = self._axes[share_y]
        ax = cast('plt.Axes', self._fig.add_subplot(self._grid[y_slice, x_slice], # type: ignore
                                                    **subplot_kwargs))
        self._axes.append(ax)
        self._ax_data.append((x_scale, y_scale, x_label, y_label, x_unit,
                              y_unit, show_legend, legend_loc, [], [], legend_bbox,
                              nb_leg_cols, leg_font_size, leg_handle_len,
                              leg_column_space))
        gp_ax_stroke_width_pt: float = self._graph_params['axes']['stroke_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_tick_maj_len_pt: float = self._graph_params['label']['tick_maj_len'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_tick_min_len_pt: float = self._graph_params['label']['tick_min_len'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_tick_width: float = self._graph_params['label']['tick_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_label_font_size: float = self._graph_params['label']['font_size'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        if label_font_size is not None:
            gp_label_font_size *= label_font_size
        for spine in ax.spines.values(): # type: ignore
            assert isinstance(spine, spi.Spine)
            spine.set_linewidth(gp_ax_stroke_width_pt) # type: ignore
            spine.set_capstyle('round') # type: ignore
        if x_spine_center:
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_position('center') # type: ignore
        elif x_spines != 'both':
            if x_spines == 'top':
                ax.spines['bottom'].set_visible(False)
            elif x_spines == 'bottom':
                ax.spines['top'].set_visible(False)
            else:
                ax.spines['bottom'].set_visible(False)
                ax.spines['top'].set_visible(False)
        if x_arrow:
            y_zero = 0
            if (y_lim is not None) & (not x_spine_center):
                assert y_lim is not None
                y_zero = y_lim[0]
            ax.plot(1, y_zero, transform=ax.get_yaxis_transform(), # type: ignore
                    clip_on=False,
                    marker=mma.MarkerStyle(
                        marker='>',
                        capstyle=men.CapStyle('round'),
                        joinstyle=men.JoinStyle('round')
                    ),
                    markersize=gp_ax_stroke_width_pt * 3,
                    markeredgewidth=gp_ax_stroke_width_pt,
                    markeredgecolor='black',
                    markerfacecolor='black',
                    zorder=1000)
        if y_spine_center:
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_position('center') # type: ignore
        elif y_spines != 'both':
            if y_spines == 'right':
                ax.spines['left'].set_visible(False)
            elif y_spines == 'left':
                ax.spines['right'].set_visible(False)
            else:
                ax.spines['left'].set_visible(False)
                ax.spines['right'].set_visible(False)
        if y_arrow:
            x_zero = 0
            if (x_lim is not None) & (not y_spine_center):
                assert x_lim is not None
                x_zero = x_lim[0]
            ax.plot(x_zero, 1, transform=ax.get_xaxis_transform(), # type: ignore
                    clip_on=False,
                    marker=mma.MarkerStyle(
                        marker='^',
                        capstyle=men.CapStyle('round'),
                        joinstyle=men.JoinStyle('round')
                    ),
                    markersize=gp_ax_stroke_width_pt * 3,
                    markeredgewidth=gp_ax_stroke_width_pt,
                    markeredgecolor='black',
                    markerfacecolor='black',
                    zorder=1000)
        x_color: str = 'black'
        if x_label_color is not None:
            if isinstance(x_label_color, int):
                gp_dat_colors: List[str] = self._graph_params['data']['cols']
                x_color = gp_dat_colors[x_label_color]
            else:
                gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                x_color = gp_dat_named_colors[x_label_color]
            ax.tick_params(axis='x', which='major', labelcolor=x_color) # type: ignore
        y_color: str = 'black'
        if y_label_color is not None:
            if isinstance(y_label_color, int):
                gp_dat_colors: List[str] = self._graph_params['data']['cols']
                y_color = gp_dat_colors[y_label_color]
            else:
                gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                y_color = gp_dat_named_colors[y_label_color]
            ax.tick_params(axis='y', which='major', labelcolor=y_color) # type: ignore
        ax.tick_params(axis='both', which='major', direction='in', # type: ignore
                       length=gp_tick_maj_len_pt, width=gp_tick_width,
                       right=True, top=True, left=True, bottom=True,
                       labelsize=gp_label_font_size)
        ax.tick_params(axis='both', which='minor', direction='in', # type: ignore
                       length=gp_tick_min_len_pt, width=gp_tick_width / 2,
                       right=True, top=True, left=True, bottom=True)
        # Set axes title:
        gp_font_family: str = self._graph_params['label']['font_name']
        gp_ax_font_size: float = self._graph_params['axes']['font_size'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        title_kwargs: Dict[str, Any] = {
            'fontfamily': gp_font_family,
            'fontsize': gp_ax_font_size,
            'fontweight': 'bold'
        }
        if title_pad is not None:
            title_kwargs['pad'] = title_pad / self._fig_dpi * 72 * self._figure_size[0]
        if title_loc is not None:
            title_kwargs['loc'] = title_loc
        if title is not None:
            ax.set_title(title, **title_kwargs) # type: ignore
        # Set axes scale:
        GraphMaker._set_scale(ax, x_scale)
        GraphMaker._set_scale(ax, y_scale, False)
        # Set tick locations:
        self._set_tick_loc(ax, x_scale, show_x_ticks, max_nb_x_ticks,
                           fixed_locs=fixed_locs_x)
        self._set_tick_loc(ax, y_scale, show_y_ticks, max_nb_y_ticks, False,
                           fixed_locs=fixed_locs_y)
        # Set axes grids:
        if x_grid | y_grid:
            gp_grid_color: str = self._graph_params['axes']['grid_col']
            gp_grid_stroke: float = self._graph_params['axes']['grid_width'] \
                / self._fig_dpi * 72 * self._figure_size[0]
            which_str: str = 'x'
            if x_grid & y_grid:
                which_str = 'both'
            elif y_grid:
                which_str = 'y'
            ax.grid(visible=True, which='major', axis=which_str, # type: ignore
                    linewidth=gp_grid_stroke, color=gp_grid_color,
                    linestyle=':', dash_capstyle='round', zorder=-20)
        # Set axis formatters:
        GraphMaker._format_tick_labels(ax, x_scale, x_unit, show_x_labels,
                                       fixed_labels=fixed_labels_x,
                                       precision=x_label_precision)
        GraphMaker._format_tick_labels(ax, y_scale, y_unit, show_y_labels, False,
                                       fixed_labels=fixed_labels_y,
                                       precision=y_label_precision)
        # Set axis labels:
        self._set_label(ax, x_label, x_label_pad,
                        label_font_size=label_font_size,
                        color=x_color)
        self._set_label(ax, y_label, y_label_pad, False,
                        label_font_size=label_font_size,
                        color=y_color)
        if x_lim is not None:
            ax.set_xlim(x_lim[0], x_lim[1])
        if y_lim is not None:
            ax.set_ylim(y_lim[0], y_lim[1])
        if x_invert:
            ax.xaxis.set_inverted(True)
        if y_invert:
            ax.yaxis.set_inverted(True)
        if hide_x_ticks:
            ax.tick_params(axis='x', which='both', length=0) # type: ignore
        if hide_y_ticks:
            ax.tick_params(axis='y', which='both', length=0) # type: ignore
        if (not x_label_bot) | x_label_top:
            ax.tick_params(axis='x', labelbottom=x_label_bot, labeltop=x_label_top) # type: ignore
            if (not x_label_bot) & x_label_top:
                ax.xaxis.set_label_position('top')
        if (not y_label_left) | y_label_right:
            ax.tick_params(axis='y', labelleft=y_label_left, labelright=y_label_left) # type: ignore
            if (not y_label_left) & y_label_right:
                ax.yaxis.set_label_position('right')
        if x_label_rotate is not None:
            ax.tick_params(axis='x', labelrotation=x_label_rotate) # type: ignore
            for label in ax.get_xticklabels():
                label.set_ha('right')
        if y_label_rotate is not None:
            ax.tick_params(axis='y', labelrotation=y_label_rotate) # type: ignore
        return len(self._axes) - 1

    def create_twin_ax_x(self, orig_ax: int, label: str, unit: str='-',
                         scale: str='lin',
                         max_nb_ticks: Optional[int]=None,
                         lim: Optional[Tuple[float, float]]=None,
                         label_font_size: Optional[float]=None,
                         label_precision: int=1,
                         label_color: Optional[Union[int, str]]=None) -> int:
        """Create twin y axis."""
        if self._grid is None:
            return -1
        axs = self._axes[orig_ax]
        ax = axs.twinx()
        self._axes.append(ax)
        orig_ax_data = self._ax_data[orig_ax]
        self._ax_data.append((orig_ax_data[0], scale, orig_ax_data[2], label,
                              orig_ax_data[4], unit, False,
                              orig_ax_data[7], [], [], *orig_ax_data[10:]))
        gp_tick_maj_len_pt: float = self._graph_params['label']['tick_maj_len'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_tick_min_len_pt: float = self._graph_params['label']['tick_min_len'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_tick_width: float = self._graph_params['label']['tick_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_label_font_size: float = self._graph_params['label']['font_size'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        if label_font_size is not None:
            gp_label_font_size *= label_font_size
        color: str = 'black'
        if label_color is not None:
            if isinstance(label_color, int):
                gp_dat_colors: List[str] = self._graph_params['data']['cols']
                color = gp_dat_colors[label_color]
            else:
                gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                color = gp_dat_named_colors[label_color]
        ax.tick_params(axis='both', which='major', direction='in', # type: ignore
                       length=gp_tick_maj_len_pt, width=gp_tick_width,
                       right=True, top=False, left=False, bottom=False,
                       labelsize=gp_label_font_size, labelcolor=color)
        ax.tick_params(axis='both', which='minor', direction='in', # type: ignore
                       length=gp_tick_min_len_pt, width=gp_tick_width / 2,
                       right=True, top=False, left=False, bottom=False)
        GraphMaker._set_scale(ax, scale, False)
        self._set_tick_loc(ax, scale, True, max_nb_ticks, False,
                           fixed_locs=None)
        GraphMaker._format_tick_labels(ax, scale, unit, True, False,
                                       fixed_labels=None, precision=label_precision)
        self._set_label(ax, label, None, False, label_font_size=label_font_size, color=color)
        if lim is not None:
            ax.set_ylim(lim[0], lim[1])
        return len(self._axes) - 1

    def int_plot(self, ax: int, ys: List[float], xs: Optional[List[float]]=None,
                 line_style: Optional[str]=None, color: Optional[int]=None,
                 marker: Optional[str]=None, marker_color: Optional[int]=None,
                 label: Optional[str]=None) -> None:
        """Plot the given ys values at discrete x-locations. If no xs array is given,
        the x-locations are: [0, 1, 2, ...]."""
        if xs is None:
            xs = list(range(len(ys)))
        axs = self._axes[ax]
        kwargs = self._build_kwargs_plot(line_style, color, marker, marker_color, label=label)
        axs.plot(xs, ys, **kwargs) # type: ignore
        # Set x scale to linear:
        GraphMaker._set_scale(axs, 'lin')
        # Set x axis tick locations:
        gp_max_nb_ticks: int = self._graph_params['label']['max_nb_ticks']
        axs.xaxis.set_minor_locator(tic.NullLocator())
        if len(xs) <= gp_max_nb_ticks:
            axs.xaxis.set_major_locator(tic.FixedLocator(xs))
        else:
            axs.xaxis.set_major_locator(tic.AutoLocator())
        # Set label font family:
        self._set_tick_label_font_fam(axs)
        # Format y tick labels and adjust label unit:
        # _, y_scale, x_label, y_label, _, y_unit, _, _ = self._ax_data[ax]
        # GraphMaker._format_tick_labels(axs, y_scale, y_unit, False)
        # self._set_label(axs, x_label)
        # self._set_label(axs, y_label, False)

    def plot(self, ax: int, xs: List[float], ys: List[float],
             line_style: Optional[str]=None, color: Optional[Union[int, str]]=None,
             marker: Optional[str]=None,
             marker_color: Optional[Union[int, str]]=None,
             marker_edge_color: Optional[Union[int, str]]=None,
             label: Optional[str]=None, alpha: float=1,
             line_width: float=1,
             visible: bool=True,
             zorder: Optional[float]=None,
             edge_alpha: Optional[float]=None) -> None:
        """Plot the given x and y data."""
        axs = self._axes[ax]
        kwargs = self._build_kwargs_plot(line_style, color, marker, marker_color,
                                         marker_edge_color,
                                         label, alpha, line_width, zorder, edge_alpha)
        l = axs.plot(xs, ys, **kwargs) # type: ignore
        if not visible:
            self._ax_data[ax][8].append(l[0])
        if label is not None:
            self._ax_data[ax][9].append(line_width)
        # Set label font family:
        self._set_tick_label_font_fam(axs)
        # Format tick labels and adjust label unit:
        # x_scale, y_scale, x_label, y_label, x_unit, y_unit, _, _ = self._ax_data[ax]

    def bar_(self, ax: int, xs: List[float], ys: List[float],
            width: Optional[Union[float, List[float]]]=None,
            bottom: Optional[Union[float, List[float]]]=None,
            align: Optional[str]=None,
            colors: Optional[Union[Union[int, str], List[Union[int, str]]]]=None,
            edge_colors: Optional[Union[Union[int, str], List[Union[int, str]]]]=None,
            label: Optional[str]=None,
            alpha: Optional[float]=None,
            line_width: float=1,
            zorder: Optional[float]=None) -> None:
        """Plot a bar graph of the given data."""
        axs = self._axes[ax]
        kwargs = self._build_kwargs_bar(width, bottom, align,
                                        colors, edge_colors, alpha, line_width,
                                        label, zorder)
        axs.bar(x=xs, height=ys, **kwargs) # type: ignore
        self._set_tick_label_font_fam(axs)

    def text(self, ax: int, x: float, y: float, s: str,
             color: Optional[Union[int, str]]=None,
             alpha: Optional[float]=None,
             rotation: Optional[float]=None,
             font_size: Optional[float]=None,
             border_color: Optional[Union[str, int]]=None,
             hor_align: str='center',
             ver_align: str='center',
             x_delta: float=0,
             y_delta: float=0,
             zorder: Optional[float]=None) -> None:
        """Print text on the axes."""
        axs = self._axes[ax]
        kwargs, color_str = self._build_kwargs_text(color, alpha, rotation, font_size,
                                                    border_color, hor_align, ver_align,
                                                    zorder)
        disp_to_data = axs.transData.inverted()
        data_to_disp = axs.transData
        pos_disp = data_to_disp.transform((x, y)) # type: ignore
        shifted_pos_disp = (pos_disp[0] + x_delta, pos_disp[1] + y_delta)
        pos_data = disp_to_data.transform(shifted_pos_disp) # type: ignore
        txt = axs.text(x=pos_data[0], y=pos_data[1], # type: ignore
                       s=(r'\textbf{' f'{s}' '}'), **kwargs)
        if color_str is not None:
            txt.set_path_effects([mpe.withStroke(linewidth=kwargs['fontsize'] / 4, # type: ignore
                                                 foreground=color_str)])

    def fill_between_y(self, ax: int, xs: List[float], y0s: Union[float, List[float]],
                       y1s: Optional[Union[float, List[float]]]=None,
                       where: Optional[List[bool]]=None,
                       color: Optional[Union[int, str]]=None, label: Optional[str]=None,
                       alpha: Optional[float]=None,
                       grad_end_color: Optional[Union[int, str]]=None,
                       grad_hor: bool=True,
                       grad_log: bool=False) -> None:
        """Fill the graph area between the curves (xs, y0s) and (xs, y1s) or (xs, 0) if y1s is None.
        Only fill if where equals True."""
        if isinstance(y0s, float):
            y0s = [y0s] * len(xs)
        if y1s is None:
            y1s = [0.0] * len(xs)
        elif isinstance(y1s, float):
            y1s = [y1s] * len(xs)
        if where is None:
            where = [True] * len(xs)
        axs = self._axes[ax]
        kwargs, start_color, end_color = self._build_kwargs_fill(color, label, alpha,
                                                                 grad_end_color)
        poly = axs.fill_between(xs, y0s, y1s, where, **kwargs) # type: ignore
        if (end_color is not None) & (start_color is not None):
            assert start_color is not None
            assert end_color is not None
            alpha_color0: str = start_color + f'{int(kwargs["alpha"] * 255 + 0.5):02x}'
            alpha_color1: str = end_color + f'{int(kwargs["alpha"] * 255 + 0.5):02x}'
            cmap_grad = mco.LinearSegmentedColormap.from_list('grad_cmap', # type: ignore
                                                              [alpha_color0, alpha_color1])
            verts = np.vstack([p.vertices # type: ignore
                               for p in poly.get_paths()]) # type: ignore
            if grad_log:
                grad_array = np.logspace(1.0, 2.0, 256) - 1
            else:
                grad_array = np.linspace(0.0, 1.0, 256)
            if grad_hor:
                grad_data = grad_array.reshape(1, -1)
            else:
                grad_data = grad_array.reshape(-1, 1)
            gradient = plt.imshow(grad_data, #type: ignore
                                  cmap=cmap_grad, aspect='auto',
                                  extent=[verts[:, 0].min(), verts[:, 0].max(), # type: ignore
                                          verts[:, 1].min(), verts[:, 1].max()]) # type: ignore
            gradient.set_clip_path(poly.get_paths()[0], transform=axs.transData) # type: ignore

    def im_show(self, ax: int, image: List[List[float]],
                xs: Optional[List[float]], ys: Optional[List[float]],
                norm: Optional['GraphMaker.ColorNorm']=None,
                norm_vmin: Optional[float]=None, norm_vmax: Optional[float]=None,
                color_map: Optional['GraphMaker.ColorMap']=None,
                color_bar: bool=False) -> None:
        """Plot the given image. Deprecated!"""
        if xs is None:
            xs = list(range(len(image[0])))
        if ys is None:
            ys = list(range(len(image)))
        color_norm: 'mco.Normalize'
        if norm == GraphMaker.ColorNorm.LOG:
            color_norm = mco.LogNorm()
        elif norm == GraphMaker.ColorNorm.SYMLOG:
            color_norm = mco.SymLogNorm(linthresh=1e-10, linscale=1, clip=True) # pylint: disable=unexpected-keyword-arg # type: ignore
        else:
            color_norm = mco.Normalize()
        if norm_vmin is not None:
            color_norm.vmin = norm_vmin
        if norm_vmax is not None:
            color_norm.vmax = norm_vmax
        c_map: 'mco.Colormap'
        if color_map is None:
            c_map = GraphMaker.ColorMap.WHITE_YELLOW_ORANGE_RED.value
        else:
            c_map = cast('mco.Colormap', color_map.value) # type: ignore
        axs = self._axes[ax]
        kwargs = self._build_kwargs_im_show(xs, ys, color_norm, c_map)
        img = axs.imshow(image, **kwargs) # type: ignore
        if color_bar:
            self._fig.colorbar(mappable=img, ax=axs) # type: ignore

    def contour_fill(self, ax: int, zs: List[List[float]],
                     xs: Optional[List[float]]=None, ys: Optional[List[float]]=None,
                     color_norm: Optional['GraphMaker.ColorNorm']=None,
                     norm_vmin: Optional[float]=None, norm_vmax: Optional[float]=None,
                     color_map: Optional['GraphMaker.ColorMap']=None,
                     color_bar: Union[bool, int]=False, nb_bins: int=10) -> None:
        """Plot a filled contour image."""
        if xs is None:
            xs = list(range(len(zs[0])))
        if ys is None:
            ys = list(range(len(zs)))
        if norm_vmin is None:
            norm_vmin = min((min(row) for row in zs))
        if norm_vmax is None:
            norm_vmax = max((max(row) for row in zs))
        level_locator: 'tic.Locator'
        tick_format: 'tic.Formatter'
        if color_norm == GraphMaker.ColorNorm.LOG:
            level_locator = tic.LogLocator(base=10, numticks=nb_bins)
            # tick_format = tic.LogFormatter(base=10, labelOnlyBase=True)
            tick_format = GraphMaker._LogFormatter('10')
        elif color_norm == GraphMaker.ColorNorm.SYMLOG:
            level_locator = GraphMaker._SymLogLocator(nb_bins=nb_bins)
            # tick_format = tic.LogFormatter(base=10, labelOnlyBase=True)
            tick_format = GraphMaker._LogFormatter('10')
        else:
            level_locator = tic.MaxNLocator(nbins=nb_bins)
            tick_format = GraphMaker._LinFormatter(unit='man')
        levels = self._generate_locator_levels(norm_vmin, norm_vmax, level_locator)
        c_map: 'mco.Colormap'
        if color_map is None:
            c_map = cast('mco.Colormap', GraphMaker.ColorMap.DEFAULT.value) # type: ignore
        else:
            c_map = cast('mco.Colormap', color_map.value) # type: ignore
        axs = self._axes[ax]
        norm = mco.BoundaryNorm(levels, ncolors=c_map.N, clip=True) # type: ignore
        cf = axs.contourf(xs, ys, zs, levels=levels, cmap=c_map, norm=norm) # type: ignore
        gp_tick_maj_len_pt: float = self._graph_params['label']['tick_maj_len'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_tick_min_len_pt: float = self._graph_params['label']['tick_min_len'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        gp_ax_stroke_width_pt: float = self._graph_params['axes']['stroke_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        tick_kwargs_maj: Dict[str, Any] = {
            'left': True,
            'which': 'major',
            'length': gp_tick_maj_len_pt * 3 / 4
        }
        tick_kwargs_min: Dict[str, Any] = {
            'left': True,
            'which': 'minor',
            'length': gp_tick_min_len_pt * 3 / 4
        }
        c_bar_axs: Optional[mla.Axes] = None
        if isinstance(color_bar, bool):
            if color_bar:
                self._fig.colorbar(mappable=cf, ax=axs, format=tick_format) # type: ignore
                c_bar_axs = axs
        else:
            c_bar_axs = self._axes[color_bar]
            self._fig.colorbar(mappable=cf, cax=c_bar_axs, format=tick_format) # type: ignore
        if c_bar_axs is not None:
            c_bar_axs.tick_params(**tick_kwargs_maj) # type: ignore
            c_bar_axs.tick_params(**tick_kwargs_min) # type: ignore
            for spine in c_bar_axs.spines.values(): # type: ignore
                assert isinstance(spine, spi.Spine)
                spine.set_linewidth(gp_ax_stroke_width_pt) # type: ignore
                # spine.set_capstyle('round') # type: ignore
                spine.set_joinstyle('round') # type: ignore

    def scatter(self, ax: int, xs: List[float], ys: List[float], color: Optional[int]=None,
                marker: Optional[str]=None, alpha: Optional[float]=None,
                label: Optional[str]=None) -> None:
        """Scatter plot the given x and y data.+
        Deprecated!"""
        axs = self._axes[ax]
        kwargs = self._build_kwargs_scatter(color, marker, alpha, label)
        axs.scatter(xs, ys, **kwargs) # type: ignore
        self._set_tick_label_font_fam(axs)

    def violin(self, ax: int, data: List[float], color: Optional[Union[int, str]]=None,
               marker: Optional[str]=None, label: Optional[str]=None, line_width: float=1,
               alpha: Optional[float]=None, position: float=1,
               vert: bool=True, width: float=0.5, show_box: bool=True, side: str='both',
               hist: bool=True, marker_color: Optional[Union[str, int]]=None,
               median_color: Optional[Union[str, int]]=None,
               add_ticks: bool=True) -> None:
        """Plot the given data in a violin plot."""
        axs = self._axes[ax]
        kwargs, color_str, fill_alpha = self._build_kwargs_violin(color, position, vert,
                                                                  width, alpha, side,
                                                                  hist)
        parts = axs.violinplot(dataset=data, **kwargs) # type: ignore
        if color_str is not None:
            parts['bodies'][0].set_facecolor(color_str) # type: ignore
        parts['bodies'][0].set_alpha(fill_alpha) # type: ignore
        if show_box:
            # gp_dat_stroke_width: float = self._graph_params['data']['stroke_width'] \
            #     / self._fig_dpi * 72 * self._figure_size[0]
            # I just used '2' instead, I don't know why this works...
            if side != 'both':
                delta_ = ((side=='high') - 0.5) * 2 * line_width * 2
                disp_to_data = axs.transData.inverted()
                data_to_disp = axs.transData
                if vert:
                    pos_disp, _ = data_to_disp.transform((position, 0)) # type: ignore
                    box_pos, _ = disp_to_data.transform((pos_disp + delta_, 0)) # type: ignore
                else:
                    _, pos_disp = data_to_disp.transform((0, position)) # type: ignore
                    _, box_pos = disp_to_data.transform((0, pos_disp + delta_)) # type: ignore
            else:
                box_pos = position
            box_kwargs = self._build_kwargs_box(position, vert, width, marker,
                                                line_width, color_str,
                                                marker_color=marker_color,
                                                median_color=median_color,
                                                add_ticks=add_ticks)
            box_parts = axs.boxplot(x=data, **box_kwargs) # type: ignore
            for capi in box_parts['caps']:
                cap_xs, cap_ys = capi.get_data()
                if vert: # For now only support vert
                    for i, xi in enumerate(cap_xs):
                        if (side == 'low') & (xi > position):
                            cap_xs[i] = box_pos # type: ignore
                        if (side == 'high') & (xi < position):
                            cap_xs[i] = box_pos # type: ignore
                    if side != 'both':
                        capi.set_xdata(cap_xs)
                else:
                    for i, yi in enumerate(cap_ys):
                        if (side == 'low') & (yi > position):
                            cap_ys[i] = box_pos # type: ignore
                        if (side == 'high') & (yi < position):
                            cap_ys[i] = box_pos # type: ignore
                    if side != 'both':
                        capi.set_ydata(cap_ys)
            box_xs, box_ys = box_parts['boxes'][0].get_data()
            # Check for wrong notch:
            box_xs_c = list(box_xs)
            box_ys_c = list(box_ys)
            if vert:
                if box_ys[2] < box_ys[1]:
                    box_ys_c[2] = box_ys[1]
                    box_ys_c[9] = box_ys[10]
                if box_ys[4] > box_ys[5]:
                    box_ys_c[4] = box_ys[5]
                    box_ys_c[7] = box_ys[6]
            else:
                if box_xs[2] < box_xs[1]:
                    box_xs_c[2] = box_xs[1]
                    box_xs_c[9] = box_xs[10]
                if box_xs[4] > box_xs[5]:
                    box_xs_c[4] = box_xs[5]
                    box_xs_c[7] = box_xs[6]
            box_xs, box_ys = box_xs_c, box_ys_c
            new_xs, new_ys = [], []
            if vert:
                if side != 'both':
                    x_half = box_pos + ((side=='high') - 0.5) * width / 4
                    x_full = box_pos + ((side=='high') - 0.5) * width / 2
                    new_xs = [box_pos, x_full, x_full, x_half, x_full, x_full, box_pos]
                    new_ys = box_ys[:7]
            else:
                if side != 'both':
                    y_half = box_pos + ((side=='high') - 0.5) * width / 4
                    y_full = box_pos + ((side=='high') - 0.5) * width / 2
                    new_ys = [box_pos, y_full, y_full, y_half, y_full, y_full, box_pos]
                    new_xs = box_xs[:7]
            if side != 'both':
                box_parts['boxes'][0].set_data((new_xs, new_ys)) # type: ignore
            else:
                box_parts['boxes'][0].set_data((box_xs, box_ys)) # type: ignore
            for whiskeri in box_parts['whiskers']:
                if vert:
                    whiskeri.set_xdata([box_pos, box_pos])
                else:
                    whiskeri.set_ydata([box_pos, box_pos])
            if vert:
                if side != 'both':
                    x_half = box_pos + ((side=='high') - 0.5) * width / 4
                    box_parts['medians'][0].set_xdata([position, x_half])
            else:
                if side != 'both':
                    y_half = box_pos + ((side=='high') - 0.5) * width / 4
                    box_parts['medians'][0].set_ydata([position, y_half])
            if box_parts['fliers']:
                nb_fliers = len(box_parts['fliers'][0].get_data()[0])
                if nb_fliers > 100:
                    data_to_disp = axs.transData
                    flier_xs: List[float] = []
                    flier_ys: List[float] = []
                    disp_xs: List[float] = []
                    disp_ys: List[float] = []
                    for xi, yi in zip(*box_parts['fliers'][0].get_data()):
                        disp_x, disp_y = data_to_disp.transform((xi, yi)) # type: ignore
                        found_close = False
                        for other_x, other_y in zip(disp_xs, disp_ys):
                            if np.sqrt((other_x - disp_x)**2 + (other_y - disp_y)**2) < 0.5:
                                found_close = True
                                break
                        if not found_close:
                            disp_xs.append(disp_x)
                            disp_ys.append(disp_y)
                            flier_xs.append(xi)
                            flier_ys.append(yi)
                    box_parts['fliers'][0].set_data((flier_xs, flier_ys)) # type: ignore
                    print(f'Detected large number of fliers: '
                        f'reduced from {nb_fliers} to {len(flier_xs)}.')
        if label is not None:
            self.fill_between_y(ax, [position], data[0], data[0], where=[False],
                                color=color, label=label)
        self._set_tick_label_font_fam(axs)

    def _build_kwargs_box(self, position: float=1, vert: bool=True,
                          width: float=0.5, marker: Optional[str]=None,
                          line_width: float=1,
                          color: Optional[str]=None,
                          marker_color: Optional[Union[str, int]]=None,
                          median_color: Optional[Union[str, int]]=None,
                          add_ticks: bool=True) \
        -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            'positions': [position],
            'vert': vert,
            'widths': [width / 2],
            'capwidths': [width / 2],
            'notch': True,
            'manage_ticks': add_ticks
        }
        if int(MPL_VERSION.split('.')[1]) >= 9: # type: ignore
            kwargs['tick_labels'] = ['']
        else:
            kwargs['labels'] = ['']
        if marker is not None:
            flier_props: Dict[str, Any] = {}
            gp_marker_size: float = self._graph_params['data']['marker_size'] \
                / self._fig_dpi * 72 * self._figure_size[0]
            flier_props['marker'] = GraphMaker.Marker[marker.upper()].value
            flier_props['markersize'] = gp_marker_size * line_width
            flier_color: Optional[str] = None
            if marker_color is not None:
                if isinstance(marker_color, int):
                    gp_dat_colors: List[str] = self._graph_params['data']['cols']
                    flier_color = gp_dat_colors[marker_color]
                else:
                    gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                    flier_color = gp_dat_named_colors[marker_color]
            else:
                if color is not None:
                    flier_color = color
            if flier_color is not None:
                flier_props['markerfacecolor'] = flier_color
                flier_props['markeredgecolor'] = flier_color
            kwargs['flierprops'] = flier_props
        else:
            kwargs['sym'] = ''
        gp_dat_stroke_width: float = self._graph_params['data']['stroke_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        box_props: Dict[str, Any] = {
            'linewidth': gp_dat_stroke_width * line_width,
            'solid_capstyle': 'round'
        }
        whisker_props: Dict[str, Any] = {
            'linewidth': gp_dat_stroke_width * line_width,
            'solid_capstyle': 'projecting'
        }
        cap_props: Dict[str, Any] = {
            'linewidth': gp_dat_stroke_width * line_width,
            'solid_capstyle': 'round'
        }
        median_props: Dict[str, Any] = {
            'linewidth': gp_dat_stroke_width * line_width,
            'solid_capstyle': 'butt'
        }
        median_color_str: Optional[str] = None
        if median_color is not None:
            if isinstance(median_color, int):
                gp_dat_colors: List[str] = self._graph_params['data']['cols']
                median_color_str = gp_dat_colors[median_color]
            else:
                gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                median_color_str = gp_dat_named_colors[median_color]
        if color is not None:
            box_props['color'] = color
            whisker_props['color'] = color
            cap_props['color'] = color
            median_props['color'] = color
        if median_color_str is not None:
            median_props['color'] = median_color_str
        kwargs['boxprops'] = box_props
        kwargs['whiskerprops'] = whisker_props
        kwargs['capprops'] = cap_props
        kwargs['medianprops'] = median_props
        return kwargs

    def _build_kwargs_violin(self, color: Optional[Union[int, str]]=None,
                             position: float=1, vert: bool=True, width: float=0.5,
                             alpha: Optional[float]=None,
                             side: str='both', hist: bool=True) \
        -> Tuple[Dict[str, Any], Optional[str], float]:
        kwargs: Dict[str, Any] = {
            'positions': [position],
            'vert': vert,
            'widths': [width],
            'showextrema': False
        }
        if int(MPL_VERSION.split('.')[1]) >= 9: # type: ignore
            kwargs['side'] = side
        else:
            if side != 'both':
                print(f'Warning, the side argument is not compatible '
                    f'with matplotlib version {MPL_VERSION}!')
        if not hist:
            kwargs['widths'] = [0]
        color_str: Optional[str] = None
        if color is not None:
            if isinstance(color, int):
                gp_dat_colors: List[str] = self._graph_params['data']['cols']
                color_str = gp_dat_colors[color]
            else:
                gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                color_str = gp_dat_named_colors[color]
        fill_alpha: float = self._graph_params['data']['fill_alpha']
        if alpha is not None:
            fill_alpha = alpha
        return kwargs, color_str, fill_alpha

    def _build_kwargs_scatter(self, color: Optional[int]=None, marker: Optional[str]=None,
                              alpha: Optional[float]=None,
                              label: Optional[str]=None) -> Dict[str, Any]:
        gp_marker_size: float = self._graph_params['data']['marker_size'] \
                / self._fig_dpi * 72 * self._figure_size[0]
        kwargs: Dict[str, Any] = {
            's': gp_marker_size * 2,
            'marker': GraphMaker.Marker.CIRCLE.value,
            'c': self._graph_params['data']['cols'][0],
            'edgecolors': 'none'
        }
        if color is not None:
            kwargs['c'] = self._graph_params['data']['cols'][color]
        if marker is not None:
            kwargs['marker'] = GraphMaker.Marker[marker.upper()].value
        if alpha is not None:
            kwargs['alpha'] = alpha
        if label is not None:
            kwargs['label'] = label
        return kwargs

    def _generate_locator_levels(self, vmin: float, vmax: float,
                                 level_locator: 'tic.Locator') -> List[float]:
        levels = cast(List[float], level_locator.tick_values(vmin, vmax)) # type: ignore
        new_levels: List[float] = []
        for index, l in enumerate(levels):
            if l < vmin:
                if levels[index + 1] > vmin:
                    new_levels.append(l)
            elif l > vmax:
                if levels[index - 1] < vmax:
                    new_levels.append(l)
            else:
                new_levels.append(l)
        return new_levels

    def _build_kwargs_im_show(self, xs: List[float], ys: List[float],
                              norm: 'mco.Normalize', c_map: 'mco.Colormap') -> Dict[str, Any]:
        extent = [xs[0], xs[-1], ys[0], ys[-1]]
        kwargs: Dict[str, Any] = {
            'interpolation': 'none',
            'filternorm': False,
            'resample': False,
            'interpolation_stage': 'rgba',
            'extent': extent,
            'norm': norm,
            'origin': 'lower',
            'cmap': c_map,
            'aspect': 'auto'
        }

        return kwargs

    def _build_kwargs_plot(self, line_style: Optional[str]=None,
                           color: Optional[Union[int, str]]=None,
                           marker: Optional[str]=None,
                           marker_color: Optional[Union[int, str]]=None,
                           marker_edge_color: Optional[Union[int, str]]=None,
                           label: Optional[str]=None,
                           alpha: float=1,
                           line_width: float=1,
                           zorder: Optional[float]=None,
                           edge_alpha: Optional[float]=None) -> Dict[str, Any]:
        if line_style is None:
            line_style_enum = GraphMaker.LineStyle.SOLID
        else:
            line_style_enum = GraphMaker.LineStyle[line_style.upper()]
        gp_dat_stroke_width: float = self._graph_params['data']['stroke_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        kwargs: Dict[str, Any] = {
            'linewidth': gp_dat_stroke_width * line_width,
            'solid_capstyle': 'round',
            'linestyle': self._scale_line_style(line_style_enum),
            'dash_capstyle': 'round',
            'alpha': alpha
        }
        if color is not None:
            if isinstance(color, int):
                gp_dat_colors: List[str] = self._graph_params['data']['cols']
                kwargs['color'] = gp_dat_colors[color]
            else:
                gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
                kwargs['color'] = gp_dat_named_colors[color]
        if marker is not None:
            gp_marker_size: float = self._graph_params['data']['marker_size'] \
                / self._fig_dpi * 72 * self._figure_size[0]
            kwargs['marker'] = GraphMaker.Marker[marker.upper()].value
            kwargs['markersize'] = gp_marker_size * line_width
            if marker_color is not None:
                gp_dat_colors = self._graph_params['data']['cols']
                gp_dat_named_colors = self._graph_params['data']['named_cols']
                if isinstance(marker_color, int):
                    m_face_color = gp_dat_colors[marker_color]
                else:
                    m_face_color = gp_dat_named_colors[marker_color]
                if marker_edge_color is not None:
                    if isinstance(marker_edge_color, int):
                        m_edge_color = gp_dat_colors[marker_edge_color]
                    else:
                        m_edge_color = gp_dat_named_colors[marker_edge_color]
                else:
                    m_edge_color = m_face_color
                kwargs['markerfacecolor'] = m_face_color
                if edge_alpha is None:
                    kwargs['markeredgecolor'] = m_edge_color
                else:
                    kwargs['markeredgecolor'] = m_edge_color + f'{int(edge_alpha * 255 + 0.5):02x}'
        if label is not None:
            kwargs['label'] = label
        if zorder is not None:
            kwargs['zorder'] = zorder
        return kwargs

    def _build_kwargs_text(self, color: Optional[Union[int, str]]=None,
                           alpha: Optional[float]=None,
                           rotation: Optional[float]=None,
                           font_size: Optional[float]=None,
                           border_color: Optional[Union[str, int]]=None,
                           hor_align: str='center', ver_align: str='center',
                           zorder: Optional[float]=None) \
        -> Tuple[Dict[str, Any], Optional[str]]:
        gp_label_font_size: float = self._graph_params['label']['font_size'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        if font_size is not None:
            gp_label_font_size *= font_size
        kwargs: Dict[str, Any] = {
            'fontsize': gp_label_font_size,
            'horizontalalignment': hor_align,
            'verticalalignment': ver_align
        }
        if zorder is not None:
            kwargs['zorder'] = zorder
        if alpha is not None:
            kwargs['alpha'] = alpha
        if color is not None:
            gp_dat_colors: List[str] = self._graph_params['data']['cols']
            gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
            if isinstance(color, int):
                kwargs['color'] = gp_dat_colors[color]
            else:
                kwargs['color'] = gp_dat_named_colors[color]
        if rotation is not None:
            kwargs['rotation'] = rotation
        color_str: Optional[str] = None
        if border_color is not None:
            gp_dat_colors = self._graph_params['data']['cols']
            gp_dat_named_colors = self._graph_params['data']['named_cols']
            if isinstance(border_color, int):
                color_str = gp_dat_colors[border_color]
            else:
                color_str = gp_dat_named_colors[border_color]
        return kwargs, color_str

    def _build_kwargs_bar(self, width: Optional[Union[float, List[float]]]=None,
                          bottom: Optional[Union[float, List[float]]]=None,
                          align: Optional[str]=None,
                          colors: Optional[Union[Union[int, str], List[Union[int, str]]]]=None,
                          edge_colors: Optional[Union[Union[int, str], List[Union[int, str]]]]=None,
                          alpha: Optional[float]=None,
                          line_width: float = 1,
                          label: Optional[str]=None,
                          zorder: Optional[float]=None) -> Dict[str, Any]:
        gp_dat_stroke_width: float = self._graph_params['data']['stroke_width'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        kwargs: Dict[str, Any] = {
            'linewidth': gp_dat_stroke_width * line_width,
        }
        face_alpha: str = ''
        if alpha is not None:
            face_alpha = f'{int(alpha * 256 + 0.5) - 1:02x}'
        else:
            face_alpha = f'{int(self._graph_params["data"]["fill_alpha"] * 255 + 0.5):02x}'
        if width is not None:
            kwargs['width'] = width
        if bottom is not None:
            kwargs['bottom'] = bottom
        if align is not None:
            kwargs['align'] = align
        if colors is not None:
            gp_dat_colors: List[str] = self._graph_params['data']['cols']
            gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
            if isinstance(colors, int):
                kwargs['color'] = gp_dat_colors[colors] + face_alpha
            elif isinstance(colors, str):
                kwargs['color'] = gp_dat_named_colors[colors] + face_alpha
            else:
                kwargs['color'] = []
                for col in colors:
                    if isinstance(col, int):
                        kwargs['color'].append(gp_dat_colors[col] + face_alpha) # type: ignore
                    else:
                        kwargs['color'].append(gp_dat_named_colors[col] + face_alpha) # type: ignore
        if edge_colors is not None:
            gp_dat_colors = self._graph_params['data']['cols']
            gp_dat_named_colors = self._graph_params['data']['named_cols']
            if isinstance(edge_colors, int):
                kwargs['edgecolor'] = gp_dat_colors[edge_colors] + 'ff'
            elif isinstance(edge_colors, str):
                kwargs['edgecolor'] = gp_dat_named_colors[edge_colors] + 'ff'
            else:
                kwargs['edgecolor'] = []
                for col in edge_colors:
                    if isinstance(col, int):
                        kwargs['edgecolor'].append(gp_dat_colors[col] + 'ff') # type: ignore
                    else:
                        kwargs['edgecolor'].append(gp_dat_named_colors[col] + 'ff') # type: ignore
        else:
            if colors is not None:
                if isinstance(kwargs['color'], str):
                    kwargs['edgecolor'] = kwargs['color'][:-2] + 'ff'
                else:
                    kwargs['edgecolor'] = [col[:-2] + 'ff'
                                           for col in kwargs['color']] # type: ignore
        if label is not None:
            kwargs['label'] = label
        if zorder is None:
            kwargs['zorder'] = 2
        else:
            kwargs['zorder'] = zorder
        return kwargs

    def _build_kwargs_fill(self, color: Optional[Union[int, str]]=None,
                           label: Optional[str]=None,
                           alpha: Optional[float]=None,
                           grad_end_color: Optional[Union[int, str]]=None) \
        -> Tuple[Dict[str, Any], Optional[str], Optional[str]]:
        gp_fill_alpha: float = self._graph_params['data']['fill_alpha']
        gp_fill_edge_width: float = self._graph_params['data']['fill_edge_width']
        if alpha is None:
            alpha_used = gp_fill_alpha
        else:
            alpha_used = alpha
        kwargs: Dict[str, Any] = {
            'alpha': alpha_used,
            'linewidth': gp_fill_edge_width
        }
        start_color: Optional[str] = None
        gp_dat_colors: List[str] = self._graph_params['data']['cols']
        gp_dat_named_colors: Dict[str, str] = self._graph_params['data']['named_cols']
        if color is not None:
            if isinstance(color, int):
                start_color = gp_dat_colors[color]
            else:
                start_color = gp_dat_named_colors[color]
            kwargs['color'] = start_color
        if label is not None:
            kwargs['label'] = label
        end_color: Optional[str] = None
        if grad_end_color is not None:
            kwargs['color'] = 'none'
            if isinstance(grad_end_color, int):
                end_color = gp_dat_colors[grad_end_color]
            else:
                end_color = gp_dat_named_colors[grad_end_color]
        return kwargs, start_color, end_color

    def _scale_line_style(self, line_style: 'GraphMaker.LineStyle') \
        -> Union[Tuple[float, Tuple[float, ...]], str]:
        if line_style == GraphMaker.LineStyle.NONE:
            return 'none'
        inner_tup = tuple(i / self._fig_dpi * 72 * self._figure_size[0]
                          for i in line_style.value[1])
        return (line_style.value[0] / self._fig_dpi * 72 * self._figure_size[0], inner_tup)

    def _set_label(self, ax: 'plt.Axes', label: Optional[str]=None,
                   label_pad: Optional[float]=None, is_x: bool=True,
                   label_font_size: Optional[float]=None,
                   color: Optional[str]=None) -> None:
        gp_label_font_name: str = self._graph_params['label']['font_name']
        gp_label_font_size: float = self._graph_params['label']['font_size'] \
            / self._fig_dpi * 72 * self._figure_size[0]
        if label_font_size is not None:
            gp_label_font_size *= label_font_size
        axs = ax.xaxis if is_x else ax.yaxis
        kwargs: Dict[str, Any] = {
            'fontfamily': gp_label_font_name,
            'fontsize': gp_label_font_size
        }
        if color is not None:
            kwargs['color'] = color
        if label_pad is not None:
            kwargs['labelpad'] = label_pad
        if label is not None:
            if is_x:
                ax.set_xlabel(label, **kwargs) # type: ignore
            else:
                ax.set_ylabel(label, **kwargs) # type: ignore
        axs.offsetText.set(fontfamily=gp_label_font_name, # type: ignore
                           fontsize=gp_label_font_size)

    @staticmethod
    def _format_tick_labels(ax: 'plt.Axes', scale: str, unit: str='-',
                            show_labels: bool=True, is_x: bool=True,
                            fixed_labels: Optional[List[str]]=None,
                            precision: int=1) -> None:
        axis = ax.xaxis if is_x else ax.yaxis
        formatter: tic.Formatter
        if not show_labels:
            plt.setp(axis.get_ticklabels(), visible=False) # type: ignore
            formatter = tic.NullFormatter()
        elif scale == 'pi':
            formatter = GraphMaker._PiFormatter()
        elif scale == 'ln':
            formatter = GraphMaker._LogFormatter('e', unit=unit)
        elif scale == 'log10':
            formatter = GraphMaker._LogFormatter('10', unit=unit)
        elif scale == 'log2':
            formatter = GraphMaker._LogFormatter('2', unit=unit)
        elif scale == 'ent':
            formatter = GraphMaker.EntFormatter(1e-4, unit=unit)
        elif (scale == 'fix') & (fixed_labels is not None):
            formatter = GraphMaker._FixedFormatter(fixed_labels, unit=unit) # type: ignore
        else:
            formatter = GraphMaker._LinFormatter(unit=unit, precision=precision)
        axis.set_major_formatter(formatter) # type: ignore

    class _FixedFormatter(tic.FixedFormatter):
        """Wrapper for FixedFormatter"""

        def __init__(self, labels: List[str], unit: str='-'):
            self._unit: str = unit
            super().__init__(labels)

        def set_locs(self, locs: List[float]) -> None: # type: ignore
            self._set_label_unit()
            super().set_locs(locs)

        def _set_label_unit(self) -> None:
            label_text = cast(str, self.axis.label.get_text()) # type: ignore
            if label_text:
                if ']' in label_text:
                    bracket_index = label_text.rfind(']')
                    if '$' in label_text:
                        dollar_index = label_text.rfind('$')
                        if dollar_index < bracket_index:
                            if '[' in label_text:
                                bracket_index = label_text.rfind('[')
                                label_text = label_text[:bracket_index]
                    else:
                        bracket_index = label_text.rfind('[')
                        label_text = label_text[:bracket_index]
                label_text = label_text.rstrip(' ')
                label_text = label_text + f' [{self._unit}]'
                self.axis.label.set_text(label_text) # type: ignore

    class _LinFormatter(tic.Formatter):
        """Format tick values for the linear scale."""

        def __init__(self, offset: float=0, order_mag: int=0, unit: str='-',
                     precision: int=1):
            self._offset = offset
            self._order_mag = order_mag
            self._unit = unit
            self._prec = precision

        @property
        def si_index(self) -> int:
            """The SI prefix index, connected with this formatter's order of magnitude."""
            return int(self._order_mag / 3) + 10

        def __call__(self, x: float, pos: Optional[int]=None) -> str:
            return self.format_data(x)

        def format_data(self, value: float) -> str:
            shifted_value = (value - self._offset) / 10**self._order_mag
            return f'{shifted_value:.{self._prec}f}'.rstrip('0').rstrip('.')

        def set_locs(self, locs: List[int]) -> None: # type: ignore
            self.locs = locs # type: ignore
            if len(self.locs) > 0:
                self._compute_offset()

        def _compute_offset(self) -> None:
            locs = self.locs
            v_min, v_max = sorted(self.axis.get_view_interval()) # type: ignore
            locs = [loc for loc in locs if (v_min <= loc) & (loc <= v_max)]
            if not locs:
                self._offset = 0
                self._order_mag = 0
            else:
                l_min, l_max = min(locs), max(locs)
                s_min, s_max = np.sign(l_min), np.sign(l_max)
                l_min, l_max = sorted((abs(l_min), abs(l_max)))
                if s_min != s_max:
                    self._offset = 0
                elif s_min == 0:
                    self._offset = 0
                else:
                    l_mid = (l_min + l_max) / 2
                    pow_10 = int(np.floor(np.log10(l_mid))) # type: ignore
                    pow_10_mult = float(np.floor(l_mid / (10**pow_10) * 1000) / 1000) # type: ignore
                    l_min_sca = l_min / (10**pow_10)
                    l_max_sca = l_max / (10**pow_10)
                    if l_max_sca - l_min_sca < 0.5:
                        self._offset = s_min * 10**pow_10 * pow_10_mult
                l_max_shifted = l_max - s_min * self._offset
                if l_max_shifted != 0:
                    self._order_mag = int(np.floor((np.log10(l_max_shifted) + 1) / 3)) * 3
                    if self._offset != 0:
                        l_min_shifted = l_min - s_min * self._offset
                    else:
                        l_min_shifted = -l_min
                    if l_max_shifted / (10**self._order_mag) \
                        - l_min_shifted / (10**self._order_mag) < 1:
                        self._order_mag -= 3
                else:
                    self._order_mag = 0
            label_text = cast(str, self.axis.label.get_text()) # type: ignore
            if label_text:
                if ']' in label_text:
                    bracket_index = label_text.rfind(']')
                    if '$' in label_text:
                        dollar_index = label_text.rfind('$')
                        if dollar_index < bracket_index:
                            if '[' in label_text:
                                bracket_index = label_text.rfind('[')
                                label_text = label_text[:bracket_index]
                    else:
                        bracket_index = label_text.rfind('[')
                        label_text = label_text[:bracket_index]
                label_text = label_text.rstrip(' ')
                label_text = label_text + f' [{GraphMaker.si_prefixes[self.si_index]}{self._unit}]'
                self.axis.label.set_text(label_text) # type: ignore

        def get_offset(self) -> str:
            """Calculate the offset."""
            if self._offset == 0:
                return ''
            power_10 = int(np.floor(np.log10(abs(self._offset)) / 3))
            offset_str = f'{self._offset / 10**(power_10 * 3):.1f}'\
                .rstrip('0').rstrip('.').lstrip('-')
            sign_str = '+' if self._offset > 0 else '-'
            return f'{sign_str}{offset_str} {GraphMaker.si_prefixes[power_10 + 10]}{self._unit}'

    class _PiFormatter(tic.Formatter):
        """Format tick values for the pi scale."""

        def __init__(self, offset: float=0, order_mag: int=0):
            self._offset = offset
            self._order_mag = order_mag
            self._unit = 'rad'

        @property
        def si_index(self) -> int:
            """The SI prefix index, connected with this formatter's order of magnitude."""
            return int(self._order_mag / 3) + 10

        def __call__(self, x: float, pos: Optional[int]=None) -> str:
            return self.format_data(x)

        def format_data(self, value: float) -> str:
            shifted_value = (value / np.pi - self._offset) / 10**self._order_mag
            value_str = f'{shifted_value:.1f}'.rstrip('0').rstrip('.')
            if value_str.lstrip('-') == '0':
                return '0'
            # return f'{value_str}π'
            pi_str = r'\textpi'
            # pi_str = r'$\texttt{\pi}$'
            # pi_str = 'π'
            return f'{value_str}{pi_str}'

        def set_locs(self, locs: List[float]) -> None: # type: ignore
            self.locs = locs
            if len(self.locs) > 0:
                self._compute_offset()

        def _compute_offset(self) -> None:
            locs = self.locs
            v_min, v_max = sorted(self.axis.get_view_interval()) # type: ignore
            locs = [loc / np.pi for loc in locs if (v_min <= loc) & (loc <= v_max)]
            if not locs:
                self._offset = 0
                self._order_mag = 0
            else:
                l_min, l_max = min(locs), max(locs)
                s_min, s_max = np.sign(l_min), np.sign(l_max)
                l_min, l_max = sorted((abs(l_min), abs(l_max)))
                if s_min != s_max:
                    self._offset = 0
                elif s_min == 0:
                    self._offset = 0
                else:
                    l_mid = (l_min + l_max) / 2
                    pow_10 = int(np.floor(np.log10(l_mid))) # type: ignore
                    pow_10_mult = float(np.floor(l_mid / (10**pow_10) * 1000) / 1000) # type: ignore
                    l_min_sca = l_min / (10**pow_10)
                    l_max_sca = l_max / (10**pow_10)
                    if l_max_sca - l_min_sca < 0.5:
                        self._offset = s_min * 10**pow_10 * pow_10_mult
                l_max_shifted = l_max - s_min * self._offset
                if l_max_shifted != 0:
                    self._order_mag = int(np.floor((np.log10(l_max_shifted) + 1) / 3)) * 3
                    if self._offset != 0:
                        l_min_shifted = l_min - s_min * self._offset
                    else:
                        l_min_shifted = -l_min
                    if l_max_shifted / (10**self._order_mag) \
                        - l_min_shifted / (10**self._order_mag) < 1:
                        self._order_mag -= 3
                else:
                    self._order_mag = 0
            label_text = cast(str, self.axis.label.get_text()) # type: ignore
            if label_text:
                if ']' in label_text:
                    bracket_index = label_text.rfind(']')
                    if '$' in label_text:
                        dollar_index = label_text.rfind('$')
                        if dollar_index < bracket_index:
                            if '[' in label_text:
                                bracket_index = label_text.rfind('[')
                                label_text = label_text[:bracket_index]
                    else:
                        bracket_index = label_text.rfind('[')
                        label_text = label_text[:bracket_index]
                label_text = label_text.rstrip(' ')
                label_text = label_text + f' [{GraphMaker.si_prefixes[self.si_index]}{self._unit}]'
                self.axis.label.set_text(label_text) # type: ignore

        def get_offset(self) -> str:
            """Calculate the offset."""
            if self._offset == 0:
                return ''
            power_10 = int(np.floor(np.log10(abs(self._offset)) / 3))
            offset_str = f'{self._offset / 10**(power_10 * 3):.3f}'\
                .rstrip('0').rstrip('.').lstrip('-')
            sign_str = '+' if self._offset > 0 else '-'
            # return f'{sign_str}{offset_str}π {GraphMaker.si_prefixes[power_10 + 10]}{self._unit}'
            pi_str = r'\textpi{}'
            return (f'{sign_str}{offset_str}{pi_str} '
                    f'{GraphMaker.si_prefixes[power_10 + 10]}{self._unit}')

    class _LogFormatter(tic.Formatter):
        """Format tick values for the log scales."""

        def __init__(self, base: str, unit: Optional[str]=None):
            self._base_str = base
            if base == 'e':
                self._base = np.exp(1)
            else:
                self._base = float(base)
            self._unit = unit

        def __call__(self, x: float, pos: Optional[int]=None) -> str:
            return self.format_data(x)

        def format_data(self, value: float) -> str:
            if value == 0:
                return '0'
            # Perform round before floor, as log might given slightly too low results.
            exp = int(np.floor(np.round(np.log(abs(value)) # type: ignore
                                        / np.log(self._base) * 100) / 100))
            if exp == 0:
                exp_str = ''
            else:
                exp_str = f'{self._base_str}\\textsuperscript{{{exp:d}}}'
            man = abs(value) / (self._base ** exp)
            man_str = f'{man:.2f}'
            if float(man_str) == 1:
                if not exp_str:
                    man_str = '1'
                else:
                    man_str = ''
            if value < 0:
                sign_str = '-'
            else:
                sign_str = ''
            return f'{sign_str}{man_str}{exp_str}'

        def set_locs(self, locs: List[int]) -> None: # type: ignore
            self.locs = locs # type: ignore
            if self._unit is None:
                return
            label_text = cast(str, self.axis.label.get_text()) # type: ignore
            if label_text:
                if ']' in label_text:
                    bracket_index = label_text.rfind(']')
                    if '$' in label_text:
                        dollar_index = label_text.rfind('$')
                        if dollar_index < bracket_index:
                            if '[' in label_text:
                                bracket_index = label_text.rfind('[')
                                label_text = label_text[:bracket_index]
                    else:
                        bracket_index = label_text.rfind('[')
                        label_text = label_text[:bracket_index]
                label_text = label_text.rstrip(' ')
                label_text = label_text + f' [{self._unit}]'
                self.axis.label.set_text(label_text) # type: ignore

    def _set_tick_loc(self, ax: 'plt.Axes', scale: str, show_ticks: bool,
                      max_nb_ticks: Optional[int]=None, is_x: bool=True,
                      fixed_locs: Optional[List[float]]=None) -> None:
        if max_nb_ticks is None:
            max_nb_ticks = int(self._graph_params['label']['max_nb_ticks'])
        axis = ax.xaxis if is_x else ax.yaxis
        if not show_ticks: # This will hide also the labels
            axis.set_major_locator(tic.NullLocator())
            axis.set_minor_locator(tic.NullLocator())
        elif scale == 'ln':
            axis.set_major_locator(tic.LogLocator(base=np.exp(1), numticks=max_nb_ticks))
        elif scale == 'log10':
            axis.set_major_locator(tic.LogLocator(base=10, numticks=max_nb_ticks))
        elif scale == 'log2':
            axis.set_major_locator(tic.LogLocator(base=2, numticks=max_nb_ticks))
        elif scale == 'pi':
            axis.set_major_locator(GraphMaker.MajorPiLocator(max_nb_ticks))
            axis.set_minor_locator(GraphMaker._MinorPiLocator(max_nb_ticks))
        elif scale == 'ent':
            axis.set_major_locator(GraphMaker.MajorEntLocator(max_nb_ticks, 1e-4))
            axis.set_minor_locator(GraphMaker.MinorEntLocator(max_nb_ticks, 1e-4))
        elif scale == 'int':
            axis.set_major_locator(tic.MultipleLocator(1)) # type: ignore
            axis.set_minor_locator(tic.NullLocator())
        elif (scale == 'fix') & (fixed_locs is not None):
            axis.set_major_locator(tic.FixedLocator(fixed_locs)) # type: ignore
            axis.set_minor_locator(tic.NullLocator())
        else:
            axis.set_major_locator(tic.AutoLocator())
            axis.set_minor_locator(tic.AutoMinorLocator())

    class _MinorPiLocator(tic.Locator):
        """Generate minor ticks for the pi scale."""

        def __init__(self, max_nb_ticks: int, num_subdivide: Optional[int]=None):
            self._max_nb_ticks = max_nb_ticks
            self._num_subdivide = num_subdivide

        def __call__(self) -> List[float]:
            v_min, v_max = self.axis.get_view_interval() # type: ignore
            return self.tick_values(v_min, v_max)

        def tick_values(self, vmin: float, vmax: float) -> List[float]:
            """Calculate the tick locations."""
            major_loc = GraphMaker.MajorPiLocator(self._max_nb_ticks)
            major_ticks = major_loc.tick_values(vmin, vmax)
            if len(major_ticks) < 2:
                return []
            major_bin_len = (major_ticks[1] - major_ticks[0]) / np.pi
            major_bin_len = int(major_bin_len / 10**int(np.log10(major_bin_len)))
            num_subdivide: int
            if self._num_subdivide is None:
                if major_bin_len == 5:
                    num_subdivide = 5
                else:
                    num_subdivide = 4
            else:
                num_subdivide = self._num_subdivide
            bin_len = (major_ticks[1] - major_ticks[0]) / num_subdivide
            major_ticks.append(major_ticks[-1] + bin_len * num_subdivide)
            result: List[float] = []
            for maj_tick in major_ticks:
                for sub in range(1, num_subdivide):
                    result.append(maj_tick - sub * bin_len)
            return result

    class MajorPiLocator(tic.Locator):
        """Generate ticks at multiples of pi."""

        def __init__(self, max_nb_ticks: int):
            self._max_nb_ticks = max_nb_ticks

        def __call__(self) -> List[float]:
            vmin, vmax = self.axis.get_view_interval() # type: ignore
            return self.tick_values(vmin, vmax)

        def tick_values(self, vmin: float, vmax: float) -> List[float]:
            """Calculate the tick locations."""
            if vmax < vmin:
                vmin, vmax = vmax, vmin
            range_len = vmax - vmin
            nb_pis = int(np.ceil(range_len / np.pi))
            pi_mult = nb_pis / self._max_nb_ticks
            pow_10 = np.floor(np.log10(pi_mult))
            sca_mult = pi_mult / (10**pow_10)
            if sca_mult < 2:
                pi_mult = 2 * 10**pow_10
            elif sca_mult < 5:
                pi_mult = 5 * 10**pow_10
            else:
                pi_mult = 10 * 10**pow_10
            result: List[float] = [np.floor(vmin / np.pi / pi_mult) * np.pi * pi_mult]
            while result[-1] < vmax:
                result.append(result[-1] + np.pi * pi_mult)
            return result

    class _SymLogLocator(tic.Locator):
        """Generate ticks with a log scale for both positive and negative values."""

        def __init__(self, nb_bins: int=10, base: float=10, lin_thresh_pow: int=-10):
            self._nb_bins = nb_bins
            self._base = base
            self._lin_thresh_pow = lin_thresh_pow

        def set_params(self, **kwargs: Dict[str, Any]) -> None:
            """
            Set parameters for this locator.
            
            Parameters
            ----------
            nb_bins : int, optional
            base : float, optional
            lin_thresh_pow : int, optional
            """
            if 'nb_bins' in kwargs:
                self._nb_bins = int(kwargs.pop('nb_bins')) # type: ignore
            if 'base' in kwargs:
                self._base = float(kwargs.pop('base')) # type: ignore
            if 'lin_thresh_pow' in kwargs:
                self._lin_thresh_pow = int(kwargs.pop('lin_thresh_pow')) # type: ignore

        def __call__(self) -> List[float]:
            vmin, vmax = self.axis.get_view_interval() # type: ignore
            return self.tick_values(vmin, vmax)

        def tick_values(self, vmin: float, vmax: float) -> List[float]:
            if (vmin >= 0) | (vmax <= 0):
                return []
            base_start = int(np.ceil(np.log(-vmin) / np.log(self._base)))
            base_end = int(np.ceil(np.log(vmax) / np.log(self._base)))
            base_range = base_start + base_end - 2 * self._lin_thresh_pow
            bin_width = int(np.ceil(base_range / (self._nb_bins - 2)))
            nb_bins_neg = int(np.ceil((base_start - self._lin_thresh_pow) / bin_width))
            nb_bins_pos = int(np.ceil((base_end - self._lin_thresh_pow) / bin_width))
            result: List[float] = []
            for i in range(nb_bins_neg + 1):
                result.append(- self._base**(self._lin_thresh_pow + (nb_bins_neg - i) * bin_width))
            result.append(0)
            for i in range(nb_bins_pos + 1):
                result.append(self._base**(self._lin_thresh_pow + i * bin_width))
            return result

        # def view_limits(self, vmin: float, vmax: float) -> Tuple[float]:
        #     return super().view_limits(vmin, vmax)

    @staticmethod
    def _set_scale(ax: 'plt.Axes', scale: str, is_x: bool=True) -> None:
        axis = ax.xaxis if is_x else ax.yaxis
        scale_base: sca.ScaleBase
        if scale == 'ln':
            scale_base = sca.LogScale(axis, base=np.exp(1), subs=[1.43, 1.86, 2.29]) # type: ignore
        elif scale == 'log10':
            scale_base = sca.LogScale(axis, base=10, subs=[2, 3, 4, 5, 6, 7, 8, 9]) # type: ignore
        elif scale == 'log2':
            scale_base = sca.LogScale(axis, base=2, subs=[0.625, 0.75, 0.875]) # type: ignore
        elif scale == 'pi':
            scale_base = sca.LinearScale(axis)
        elif scale == 'ent':
            scale_base = GraphMaker.EntScale(axis)
        elif scale == 'fix':
            scale_base = sca.LinearScale(axis)
        else:
            scale_base = sca.LinearScale(axis)
        if is_x:
            ax.set_xscale(scale_base) # type: ignore
        else:
            ax.set_yscale(scale_base) # type: ignore

    class EntTransform(mtr.Transform):
        """Entropy transform."""

        input_dims = output_dims = 1

        def __init__(self, min_entropy: float):
            super().__init__('ent')
            self._min_entropy = min_entropy

        def transform_non_affine(self, values): # type: ignore
            values[values < self._min_entropy] = self._min_entropy # type: ignore
            values[values > 1 - self._min_entropy] = 1 - self._min_entropy # type: ignore
            with np.errstate(divide="ignore", invalid="ignore"):
                result = np.log2(values / (1 - values)) # type: ignore
                return result

        def inverted(self) -> 'mtr.Transform':
            return GraphMaker.InvEntTransform(self._min_entropy)

    class InvEntTransform(mtr.Transform):
        """Inverted entropy transform."""

        input_dims = output_dims = 1

        def __init__(self, min_entropy: float):
            super().__init__()
            self._min_entropy = min_entropy

        def transform_non_affine(self, values): # type: ignore
            result = np.power(2, values) / (1 + np.power(2, values))
            return result

        def inverted(self) -> 'mtr.Transform':
            return GraphMaker.EntTransform(self._min_entropy)

    class EntScale(sca.ScaleBase):
        """Entropy log scale at zero and one."""

        name = 'ent'
        _min_entropy = 1e-4

        def set_default_locators_and_formatters(self, axis: mxs.Axis) -> None:
            axis.set_major_locator(GraphMaker.MajorEntLocator(11, self._min_entropy))
            axis.set_minor_locator(GraphMaker.MinorEntLocator(11, self._min_entropy))
            axis.set_major_formatter(GraphMaker.EntFormatter(self._min_entropy, # type: ignore
                                                             'bit'))

        def get_transform(self) -> 'mtr.Transform':
            return GraphMaker.EntTransform(self._min_entropy)

        def limit_range_for_scale(self, vmin: float, vmax: float, minpos: float) \
            -> Tuple[float, float]:
            return (max(self._min_entropy, vmin), min(1 - self._min_entropy, vmax))

    class MajorEntLocator(tic.Locator):
        """Generate ticks for the entropy scale."""

        def __init__(self, max_nb_ticks: int, min_entropy: float):
            self._max_nb_ticks = max_nb_ticks
            self._min_entropy = min_entropy

        def __call__(self) -> List[float]:
            vmin, vmax = self.axis.get_view_interval() # type: ignore
            return self.tick_values(vmin, vmax)

        def tick_values(self, vmin: float, vmax: float) -> List[float]:
            """Calculate the tick locations."""
            result: List[float]
            if self._max_nb_ticks >= 17:
                result = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 0.2, 0.3, 0.4]
            elif self._max_nb_ticks >= 11:
                result = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
            elif self._max_nb_ticks >= 7:
                result = [1e-5, 1e-1, 0.25]
            else:
                result = [self._min_entropy]
            final_result: List[float] = []
            for r in result:
                if r < self._min_entropy:
                    continue
                final_result.append(r)
                final_result.append(1 - r)
            final_result.append(0.5)
            result = sorted(final_result)
            final_result = []
            for i, r in enumerate(result):
                if r > vmax:
                    if i > 0:
                        if result[i - 1] > vmax:
                            continue
                if r < vmin:
                    if i < len(result) - 1:
                        if result[i + 1] < vmin:
                            continue
                final_result.append(r)
            return sorted(final_result)

    class MinorEntLocator(tic.Locator):
        """Generate minor ticks for the entropy scale."""

        def __init__(self, max_nb_ticks: int, min_entropy: float):
            self._max_nb_ticks = max_nb_ticks
            self._min_entropy = min_entropy

        def __call__(self) -> List[float]:
            v_min, v_max = self.axis.get_view_interval() # type: ignore
            return self.tick_values(v_min, v_max)

        def tick_values(self, vmin: float, vmax: float) -> List[float]:
            """Calculate the tick locations."""
            maj_loc = GraphMaker.MajorEntLocator(self._max_nb_ticks, self._min_entropy)
            maj_locs = maj_loc.tick_values(vmin, vmax)
            result: List[float] = []
            for l_start, l_end in zip(maj_locs, maj_locs[1:]):
                int_width = (l_end - l_start) / 4
                for i in range(3):
                    result.append(l_start + int_width * (i + 1))
            return result

    class EntFormatter(tic.Formatter):
        """Format tick values for the entropy scales."""

        def __init__(self, max_ent: float, unit: Optional[str]=None):
            self._max_ent = max_ent
            self._unit = unit

        def __call__(self, x: float, pos: Optional[int]=None) -> str:
            return self.format_data(x)

        def format_data(self, value: float) -> str:
            if abs(value - 0.5) <= 0.4:
                return f'{value:3.1f}'
            if value >= 1 - self._max_ent:
                return '1'
            if value <= self._max_ent:
                return '0'
            return f'{value:f}'.rstrip('0')

        def set_locs(self, locs: List[int]) -> None: # type: ignore
            self.locs = locs # type: ignore
            if self._unit is None:
                return
            label_text = cast(str, self.axis.label.get_text()) # type: ignore
            if label_text:
                if ']' in label_text:
                    bracket_index = label_text.rfind(']')
                    if '$' in label_text:
                        dollar_index = label_text.rfind('$')
                        if dollar_index < bracket_index:
                            if '[' in label_text:
                                bracket_index = label_text.rfind('[')
                                label_text = label_text[:bracket_index]
                    else:
                        bracket_index = label_text.rfind('[')
                        label_text = label_text[:bracket_index]
                label_text = label_text.rstrip(' ')
                label_text = label_text + f' [{self._unit}]'
                self.axis.label.set_text(label_text) # type: ignore

    # @staticmethod
    # def _tick_formatter(value: float, scale: str, factor: int) -> str:
    #     if value == 0:
    #         return '0'
    #     if scale == 'lin':
    #         return f'{value / factor:.1f}'.rstrip('0').rstrip('.')
    #     if scale == 'ln':
    #         pow_e = int(np.log(value))
    #         return f'e\\textsuperscript{{{pow_e:d}}}' # pylint: disable=anomalous-backslash-in-string
    #     if scale == 'log10':
    #         pow_10 = int(np.log10(value))
    #         return f'10\\textsuperscript{{{pow_10:d}}}' # pylint: disable=anomalous-backslash-in-string
    #     if scale == 'log2':
    #         pow_2 = int(np.log2(value))
    #         return f'2\\textsuperscript{{{pow_2:d}}}' # pylint: disable=anomalous-backslash-in-string
    #     return str(value)

    def _set_tick_label_font_fam(self, ax: 'plt.Axes') -> None:
        gp_label_font_name: str = self._graph_params['label']['font_name']
        for label in ax.get_xticklabels():
            label.set(fontfamily=gp_label_font_name)
        for label in ax.get_yticklabels():
            label.set(fontfamily=gp_label_font_name)

    def _set_legend_all_axs(self) -> None:
        for axs, (_, _, _, _, _, _, show_legend, loc, lines_remove, lines_width, leg_bbox,
                  nb_leg_cols, leg_font_size, leg_handle_len, leg_column_space) \
            in zip(self._axes, self._ax_data):
            if show_legend:
                gp_font_size: float = self._graph_params['legend']['font_size'] \
                    / self._fig_dpi * 72 * self._figure_size[0]
                gp_handle_scale: float = self._graph_params['legend']['handle_scale']
                gp_font_name: str = self._graph_params['legend']['font_name']
                gp_handle_len: float = self._graph_params['legend']['handle_len']
                gp_line_width: float = self._graph_params['data']['stroke_width'] \
                    / self._fig_dpi * 72 * self._figure_size[0]
                gp_face_color: str = self._graph_params['legend']['face_color']
                gp_edge_color: str = self._graph_params['legend']['edge_color']
                gp_frame_width: float = self._graph_params['legend']['frame_width'] \
                    / self._fig_dpi * 72 * self._figure_size[0]
                gp_frame_alpha: float = self._graph_params['legend']['frame_alpha']
                leg_kwargs: Dict[str, Any] = {
                    'prop': {'family': gp_font_name, 'size': gp_font_size * leg_font_size},
                    'markerscale': gp_handle_scale,
                    'handlelength': gp_handle_len,
                    'fancybox': False,
                    'facecolor': gp_face_color,
                    'edgecolor': gp_edge_color,
                    'framealpha': gp_frame_alpha,
                    'loc': loc
                }
                if leg_handle_len is not None:
                    leg_kwargs['handlelength'] *= leg_handle_len
                if leg_bbox is not None:
                    leg_kwargs['bbox_to_anchor'] = tuple(leg_bbox)
                if nb_leg_cols is not None:
                    leg_kwargs['ncols'] = nb_leg_cols
                if leg_column_space is not None:
                    leg_kwargs['columnspacing'] = leg_column_space
                leg = axs.legend(**leg_kwargs) # type: ignore
                for l in lines_remove:
                    l.remove()
                # Scale down line width as well:
                for leg_line, line_width in zip(leg.get_lines(), lines_width):
                    leg_line.set_linewidth(gp_line_width * line_width * gp_handle_scale)
                # Set legend frame:
                leg.get_frame().set(linewidth=gp_frame_width, joinstyle='round') # type: ignore

    def write_svg(self) -> None:
        """Store this graph."""
        self._set_legend_all_axs()
        self._fig.savefig(os.path.join(self._folder_name, 'svg', self._file_name)) # type: ignore

    class LineStyle(Enum):
        """An enum class holding the supported line styles."""

        SOLID = (0, (1, 0))
        DOTTED = (0, (0.01, 4.5))
        DASHED = (0, (6, 4.5))
        DASHDOTTED = (0, (6, 4.5, 0.01, 4.5))
        DASHDOTDOTTED = (0, (6, 4.5, 0.01, 4.5, 0.01, 4.5))
        NONE = 'none'

    class Marker(Enum):
        """An enum class holding the supported marker styles."""

        DOT = '.'
        CIRCLE = 'o'
        TRI_DOWN = 'v'
        TRI_UP = '^'
        TRI_LEFT = '<'
        TRI_RIGHT = '>'
        SQUARE = 's'
        PENTAGON = 'p'
        STAR = '*'
        DIAMOND = 'D'
        PLUS = 'P'
        CROSS = 'X'

    class ColorNorm(Enum):
        """An enum class holding the supported color normalizer scales."""

        LIN = 'lin'
        LOG = 'log'
        SYMLOG = 'symlog'

    class ColorMap(Enum):
        """An enum class holding the supported color maps."""

        BLUE_WHITE_RED = mco.LinearSegmentedColormap.from_list('blue_white_red', # type: ignore
                                                               ['#3498db', '#ffffff', '#e74c3c'])
        WHITE_YELLOW_ORANGE_RED \
            = mco.LinearSegmentedColormap.from_list('wh_ye_or_rd', # type: ignore
                                                    ['#ffffff', '#f7dc6f', '#e59866', '#e74c3c'])
        DEFAULT = cast('mco.Colormap', plt.colormaps['YlOrRd']) # type: ignore
