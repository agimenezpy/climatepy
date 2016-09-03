import ConfigParser as cfgParser
import logging as log
import os
from os import path as pth

import numpy as np
import pandas as pd

from climatepy.analysis.regression import aproximate_lineal, aproximate
from climatepy.figures import DateLineGraph
from climatepy.scenario.export_xls import get_column_names

__author__ = 'agimenez'


def draw_line_asc(filename, data_file,
                  model, escenario, year_ini, year_end, shape_file,
                  out_dir, map_key, name_prop, var_name, pos=1, title=""):
    config = cfgParser.ConfigParser()
    config.read(filename)
    var_name = var_name.upper()
    out_dict = {"sep": os.sep, "period": "%d_%d" % (year_ini, year_end),
                "step": (year_end - year_ini + 1),
                'var': var_name,
                "model": model,
                "escenario": escenario}
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    items = dict(config.items(var_name))
    yi, ye = year_ini - 1961, year_end - 1961 + 1
    myline = DateLineGraph(var_name, (year_ini, year_end + 1), **items)
    data = pd.read_csv(data_file, index_col=0, header=0)
    names = get_column_names(shape_file, map_key, name_prop)
    for idx, key in enumerate(data.columns):
        clave, nombre = key, names[key]
        if '.' in clave:
            clave = clave.split(".")[pos]
        if isinstance(nombre, tuple):
            title, nombre = nombre
        myline.set_title(unicode("%s - %s" % (title, nombre), "utf-8"))
        avg_data = data.iloc[yi:ye, idx].values

        t = np.linspace(1, avg_data.shape[0], avg_data.shape[0])
        if avg_data[avg_data < -999000].size > 0:
            avg_data[avg_data < -999000] = avg_data[avg_data > -999000].mean()
        if var_name == "PREC":
            mult = 1  # conv.get(u(items["unit"]), 1)
            color = 'b'
            avg_data *= mult
        else:
            color = 'r'
        val = aproximate(t, avg_data)
        if val is None:
            val = aproximate_lineal(t, avg_data)

        out_dict["period"] = "%d_%d" % (yi, ye)
        out_dict["region"] = clave
        log.info("%s periodo %d, %d", key, yi, ye)
        myline.add_line(avg_data, color, label=out_dict["escenario"])
        myline.add_line(val, 'k')
        myline.add_legend([escenario, "Tendencia"], 0.5)
        myline.draw(pth.join(out_dir, out_tmpl % out_dict))
        myline.clear()
