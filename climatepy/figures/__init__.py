__author__ = 'agimenez'

__all__ = ["MPLMap", "DateLineGraph", "StyleMixin", "DrawMixin", "MonthLineGraph"]

FIGURE_SIZE = [10.24, 7.68]
FONT_SIZE = "medium"
FONT_NAME = "Trebuchet MS"
FORMAT = "png"

import os.path as pth
import matplotlib.pyplot as plt


class Style(object):
    __styles = {
        "axis": {"fontsize": "x-small", "linewidth": 0.5},
        "title": {"fontsize": "large"},
        "suptitle": {"fontsize": 20, "color": "#8B2323", "family": "Verdana", "fontweight": "bold"},
        "colorbar": {"fontsize": "small"},
        "colorline": {"fontsize": 8, "linewidth": 0.2},
        "shapetext": {"fontsize": 10, "color": "k"}
    }

    def __init__(self, file_name):
        new_style = {}

        if pth.exists(file_name):
            with open(file_name) as file_style:
                for row in file_style:
                    lhs, rhs = row.split("=")
                    key, prop = lhs.split(".")
                    key = key.strip()
                    if key not in new_style:
                        new_style[key] = {}
                    prop = prop.strip()
                    rhs = rhs.strip()
                    try:
                        new_style[key][prop] = float(rhs)
                    except:
                        new_style[key][prop] = rhs
            self.__styles = new_style

    def get(self, key):
        return self.__styles[key]


class StyleMixin(object):
    __style = None

    @classmethod
    def style(cls, sty):
        if cls.__style is None:
            cls.__style = Style(cls.__name__ + ".sty")
        return cls.__style.get(sty)


class DrawMixin(object):
    def clear(self):
        pass

    def draw(self, file_name, show=False):
        if not show and not pth.exists(file_name):
            plt.savefig(file_name + "." + FORMAT)
        else:
            plt.show()

from .map import MPLMap
from .line import DateLineGraph, MonthLineGraph