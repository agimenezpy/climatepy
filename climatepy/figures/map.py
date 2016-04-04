# -*- coding: utf-8 -*-
import matplotlib.cm as cmap
import matplotlib.pyplot as plt
import mpl_toolkits.basemap as bmap
from climatepy.figures import (StyleMixin, DrawMixin, FIGURE_SIZE, FONT_NAME,
                               FONT_SIZE, FORMAT)
import numpy as np
import abc
import fiona

from matplotlib import rcParams
rcParams['legend.fontsize'] = FONT_SIZE
rcParams['font.family'] = FONT_NAME
rcParams['ytick.labelsize'] = "small"
rcParams['xtick.labelsize'] = "small"

__author__ = 'agimenez'

class BaseMap(StyleMixin, DrawMixin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, bounds, **kwargs):
        opts = kwargs or {}
        self.bounds = [0, 0, 0, 0]
        if len(bounds) > 1 and isinstance(bounds[0], tuple) \
           and isinstance(bounds[1], tuple):
            self.bounds = []
            self.bounds.extend(bounds[0])
            self.bounds.extend(bounds[1])
        self.name = name
        self.title = opts.get("title", "Demo Map").decode("UTF-8")
        self.color_map = cmap.get_cmap(opts.get("cmap", "Blues"))
        self.alt_color_map = cmap.get_cmap(opts.get("acmap", "BrBG"))
        self.levels = (int(opts.get("level_min", 0)),
                       int(opts.get("level_max", 10)),
                       int(opts.get("level_int", 11)))
        self.color_line = cmap.get_cmap(opts.get("lcolors", "YlGn_r"))
        self.alt_color_line = cmap.get_cmap(opts.get("lcolors", "YlGn_r"))
        self.color = opts.get("mpcolor", "k")

    @abc.abstractmethod
    def add_shape(self, name, file_name, field_name, linewidth=0.2, color="k"):
        pass

    @abc.abstractmethod
    def add_contour(self, x, y, data, unit=False, lines=True, alt=False,
                    extend="neither"):
        pass


class MPLMap(BaseMap):
    def __init__(self, name, bounds, **kwargs):
        super(MPLMap, self).__init__(name, bounds, **kwargs)
        self.figure = self.axes = self.map = None
        self.clear()

    def set_title(self, in_str):
        self.axes.set_title(in_str, **MPLMap.style("title"))

    def add_shape(self, name, file_name, field_name, linewidth=0.2, color="k"):
        self.map.readshapefile(file_name, name, linewidth=linewidth,
                               color=color)
        self.draw_points(file_name, field_name)

    def draw_points(self, file_name, field_name, points=False, sty=None):
        if sty is None:
            sty = MPLMap.style("shapetext")
        with fiona.open(file_name + "_pt.shp") as shp:
            for row in shp:
                geom = row["geometry"]
                x, y = geom["coordinates"][0], geom["coordinates"][1]
                if (x < self.bounds[0] or x > self.bounds[2]) or \
                        (y < self.bounds[1] or y > self.bounds[3]):
                    continue
                if points:
                    self.axes.plot(x, y, 'o', color='#cccccc')
                self.axes.text(x, y,
                               row["properties"][field_name].replace(" ", "\n"),
                               ha="center", va="center", rotation=0,
                               **sty)

    def add_contour(self, x, y, data, unit=False, lines=True, alt=False,
                    extend="neither"):
        # Options for extends are neither or both
        if len(self.levels) == 3:
            levels = np.linspace(*self.levels)
        else:
            levels = self.levels

        color_map = self.color_map
        if not alt:
            color_map = self.alt_color_map
        cs = self.axes.contourf(x, y, data, levels, cmap=color_map,
                                extend=extend)
        cbar = self.figure.colorbar(cs, ticks=cs.levels, drawedges=True,
                                    shrink=0.78, pad=0.01)
        if isinstance(unit, basestring) or isinstance(unit, unicode):
            cbar.set_label(unit, position=(0, 1), rotation="horizontal",
                           **MPLMap.style("colorbar"))
        if lines:
            color_map = self.color_line
            if not alt:
                color_map = self.alt_color_line
            cs2 = self.axes.contour(x, y, data, levels, cmap=color_map,
                                    **MPLMap.style("colorline"))
            self.axes.clabel(cs2, cs.levels, inline=True, fmt='%.0f', lw=1,
                             **MPLMap.style("colorline"))
            cbar.add_lines(cs2)

    def clear(self):
        # Warning de variables no inicializadas en el constructor
        if self.figure is not None:
            plt.close()
        self.figure = plt.figure(figsize=FIGURE_SIZE)
        self.figure.subplots_adjust(top=1, right=1, left=0.07, bottom=0)
        self.axes = self.figure.add_subplot(111)
        self.map = bmap.Basemap(llcrnrlon=self.bounds[0],
                                llcrnrlat=self.bounds[1],
                                urcrnrlon=self.bounds[2],
                                urcrnrlat=self.bounds[3])
        self.map.drawparallels(np.arange(self.bounds[1], self.bounds[3], 1),
                               labels=[1, 0, 0, 0], **MPLMap.style("axis"))
        self.map.drawmeridians(np.arange(self.bounds[0], self.bounds[2], 1),
                               labels=[0, 0, 0, 1], **MPLMap.style("axis"))
        self.axes.set_xlim(self.bounds[0], self.bounds[2])
        self.axes.set_ylim(self.bounds[1], self.bounds[3])
        #self.axes.set_xlabel("\n\nlongitud")
        #self.axes.set_ylabel("latitud\n\n")
        #self.figure.suptitle(self.title, **MPLMap.style("suptitle"))

