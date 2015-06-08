# -*- coding: utf-8 -*-
__author__ = 'agimenez'
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, DateFormatter
import datetime
import numpy as np
import abc
from climatepy.figures import StyleMixin, DrawMixin
from calendar import month_name
import locale
import sys

class LineGraph(StyleMixin, DrawMixin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, **kwargs):
        opts = kwargs or {}
        self.name = name
        self.title = opts.get("title", "Demo Map").decode("UTF-8")
        self.unit = opts.get("unit", "NN")
        self.levels = (int(opts.get("level_min", 0)),
                       int(opts.get("level_max", 10)))

    @abc.abstractmethod
    def add_line(self, data, color="k", style="-"):
        pass


class DateLineGraph(LineGraph):

    def __init__(self, name, years, **kwargs):
        super(DateLineGraph, self).__init__(name, **kwargs)
        self.figure = self.axes = self.line = None
        self.dates = np.array([datetime.date(i, 1, 1) for i in xrange(years[0], years[1])])
        self.clear()

    def add_legend(self, legend, alpha=1):
        leg = self.axes.legend(legend, "upper center", shadow=True)
        leg.get_frame().set_alpha(alpha)

    def set_title(self, in_str):
        self.axes.set_title(in_str, DateLineGraph.style("title"))

    def set_lims(self, ymin, ymax):
        self.axes.set_ylim(ymin, ymax)

    def clear(self):
        if self.figure is not None:
            plt.close()
        self.figure = plt.figure()
        self.figure.subplots_adjust(top=0.88, bottom=0.11, left=0.08, right=0.96)
        self.axes = self.figure.add_subplot(111)
        datemin = datetime.date(self.dates[0].year - 1, 1, 1)
        self.axes.set_xlim(datemin, self.dates[-1])
        self.axes.set_ylim(self.levels[0], self.levels[1])
        year = YearLocator()
        loc = YearLocator(10)
        fmt = DateFormatter("%Y")
        self.axes.xaxis.set_major_locator(loc)
        self.axes.xaxis.set_major_locator(loc)
        self.axes.xaxis.set_major_formatter(fmt)
        self.axes.xaxis.set_minor_locator(year)
        self.figure.autofmt_xdate()
        self.axes.set_ylabel(unicode(self.unit, "utf-8"))
        self.axes.set_xlabel(unicode("Años", "utf-8"))
        self.figure.suptitle(self.title, **DateLineGraph.style("suptitle"))
        self.axes.grid(True)

    def add_line(self, data, color='k', style='-'):
        self.axes.plot_date(self.dates[:len(data)], data, color + style)


class MonthLineGraph(LineGraph):

    def __init__(self, name, **kwargs):
        super(MonthLineGraph, self).__init__(name, **kwargs)
        self.figure = self.axes = self.line = None
        locale.setlocale(locale.LC_ALL, "es_PY" if sys.platform != "win32" else "Spanish")
        self.dates = np.array([month_name[i].title() for i in range(1, 13)])
        locale.setlocale(locale.LC_ALL, "C")
        self.clear()

    def add_legend(self, legend, alpha=1):
        leg = self.axes.legend(legend, "upper center", shadow=True)
        leg.get_frame().set_alpha(alpha)

    def set_title(self, in_str):
        self.axes.set_title(in_str, MonthLineGraph.style("title"))

    def set_lims(self, ymin, ymax):
        self.axes.set_ylim(ymin, ymax)

    def clear(self):
        if self.figure is not None:
            plt.close()
        self.figure = plt.figure()
        self.figure.subplots_adjust(top=0.88, bottom=0.11, left=0.08, right=0.96)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlim(0, 13)
        self.axes.set_xticks(range(1, 13))
        self.axes.set_ylim(self.levels[0], self.levels[1])
        self.axes.set_xticklabels(self.dates)
        self.figure.autofmt_xdate()
        self.axes.set_ylabel(unicode(self.unit, "utf-8"))
        self.axes.set_xlabel(unicode("Meses", "utf-8"))
        self.figure.suptitle(self.title, **DateLineGraph.style("suptitle"))
        self.axes.grid(True)

    def add_line(self, data, color='k', style='-'):
        self.axes.plot(range(1, len(data)+1), data, color + style)

    def add_bar(self, data, color='k', style='-'):
        self.axes.bar(range(1, len(data)+1), data, facecolor=color, align="center")