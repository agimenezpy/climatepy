__author__ = 'agimenez'
from climatepy.figures import DateLineGraph
from climatepy.data import ShapeMask
#from climatepy.regression import aproximate, aproximate_lineal
from climatepy.analysis.regression import aproximate, aproximate_lineal, aproximate_poly
import pandas as pd
from proceso import get_eta_data, SHP_DIR, OUTPUT_DIR, with_config
import os.path as pth
import numpy as np


@get_eta_data("line_config.ini", 1961, 2050)
def draw_escenario(config, out_dict, data, shape_file, key, pos=1):
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    items = dict(config.items(var_name))
    times = data.getTime().asComponentTime()
    yi, ye = times[0].year, times[-1].year
    myline = DateLineGraph(var_name, (yi, ye), **items)
    mascaras = ShapeMask(shape_file, key,
                         data.getLongitude(), data.getLatitude(), 0.1, False)
    for key in mascaras.keys():
        mask = mascaras[key]
        clave, nombre = key.split(":")
        clave = clave.split(".")[pos]
        myline.set_title("Escenario %s - %s" % (out_dict["escenario"], nombre))
        avg_data = []
        for idx, year in enumerate(xrange(yi, ye)):
            masked_data = np.ma.array(data[idx], mask=mask)
            avg_data.append(masked_data.mean())

        t = np.linspace(1, len(avg_data), len(avg_data))
        val = aproximate(t, avg_data)
        if val is None:
            val = aproximate_lineal(t, avg_data)

        out_dict["period"] = "%d_%d" % (yi, ye)
        print key, yi, ye
        out_dict["region"] = clave
        if var_name == "PREC":
            color = 'b'
        else:
            color = 'r'
        myline.add_line(avg_data, color)
        myline.add_line(val, 'k')
        myline.add_legend((out_dict["escenario"], ), 0.5)
        myline.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))
        myline.clear()

@with_config("line_config.ini", 1961, 2050)
def draw_line_asc(config, out_dict, year_ini, year_end, data_file, var_name, pos=1, title=""):
    out_dict['var'] = var_name
    out_dict["model"], out_dict["escenario"] = "ETA", "RCP45"
    var_name = var_name.upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    items = dict(config.items(var_name))
    yi, ye = year_ini, year_end
    myline = DateLineGraph(var_name, (yi, ye+1), **items)
    data = pd.read_csv(data_file, index_col=0, header=0)
    for idx, key in enumerate(data.columns):
        clave, nombre = key.split(":")
        clave = clave.split(".")[pos]
        myline.set_title("%s - %s" % (title, unicode(nombre, "utf-8")))
        avg_data = data.values[:, idx]
        if var_name == "PREC":
            avg_data *= 365  # to mm/year

        t = np.linspace(1, avg_data.shape[0], avg_data.shape[0])
        val = aproximate(t, avg_data)
        if val is None:
            val = aproximate_lineal(t, avg_data)

        out_dict["period"] = "%d_%d" % (yi, ye)
        print key, yi, ye
        out_dict["region"] = clave
        if var_name == "PREC":
            color = 'b'
        else:
            color = 'r'
        myline.add_line(avg_data, color)
        myline.add_line(val, 'k')
        myline.add_legend((out_dict["escenario"], ), 0.5)
        myline.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))
        myline.clear()

if __name__ == '__main__':
    #draw_escenario(pth.join(SHP_DIR, "shp", "tarija_region.shp"), "%(HASC_2)s:%(NAME_0)s - %(NAME_1)s")
    #draw_escenario(pth.join(SHP_DIR, "shp", "tarija.shp"), "%(HASC_2)s:%(NAME_1)s - %(NAME_2)s", 2)
    #draw_line_asc(pth.join(OUTPUT_DIR, "anual_sdv_prec.csv"), "prec", 0, "Sistema de Vida")
    #draw_line_asc(pth.join(OUTPUT_DIR, "anual_sdv_temp.csv"), "tp2m", 0, "Sistema de Vida")
    draw_line_asc(pth.join(OUTPUT_DIR, "anual_muni_prec.csv"), "prec", 0, "Municipio")
    draw_line_asc(pth.join(OUTPUT_DIR, "anual_muni_temp.csv"), "tp2m", 0, "Municipio")
