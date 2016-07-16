import os
from os import path as pth
import pandas as pd
import numpy as np
import ConfigParser as cfgParser
import logging as log
from climatepy.figures import DateLineGraph
from climatepy.scenario.export_xls import get_column_names
from climatepy.analysis.regression import aproximate_lineal, aproximate

__author__ = 'agimenez'


def draw_line_asc(filename, data_file,
                  model, escenario, year_ini, year_end, shape_file,
                  out_dir, map_key, name_prop, var_name, pos=1, title=""):
    config = cfgParser.ConfigParser()
    config.read(filename)
    out_dict = {"sep": os.sep, "period": "%d_%d" % (year_ini, year_end),
                "step": (year_end - year_ini + 1),
                'var': var_name,
                "model": model,
                "escenario": escenario}
    var_name = var_name.upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    items = dict(config.items(var_name))
    yi, ye = year_ini, year_end
    myline = DateLineGraph(var_name, (yi, ye+1), **items)
    data = pd.read_csv(data_file, index_col=0, header=0)
    names = get_column_names(shape_file, data.columns, map_key, name_prop)
    for idx, key in enumerate(data.columns):
        clave, nombre = key, names[idx]
        clave = clave.split(".")[pos]
        myline.set_title("%s - %s" % (title, unicode(nombre, "utf-8")))
        avg_data = data.values[:, idx]

        t = np.linspace(1, avg_data.shape[0], avg_data.shape[0])
        if avg_data[avg_data < -999000].size > 0:
            avg_data[avg_data < -999000] = avg_data[avg_data > -999000].mean()
        val = aproximate(t, avg_data)
        if val is None:
            val = aproximate_lineal(t, avg_data)

        out_dict["period"] = "%d_%d" % (yi, ye)
        out_dict["region"] = clave
        log.info("%s periodo %d, %d", key, yi, ye)
        if var_name == "PREC":
            color = 'b'
        else:
            color = 'r'
        myline.add_line(avg_data, color, label=out_dict["escenario"])
        myline.add_line(val, 'k')
        myline.add_legend([], 0.5)
        myline.draw(pth.join(out_dir, out_tmpl % out_dict))
        myline.clear()
