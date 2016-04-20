from proceso import BOUNDS, SHP_DIR, OUTPUT_DIR, get_eta_data, get_cru_data, get_eta_data_month
import os.path as pth
from climatepy.figures import MPLMap, MonthLineGraph
from climatepy.data import ShapeMask
import numpy as np
from regrid2 import Regridder
import logging as log
import pandas as pd
import calendar

__author__ = 'agimenez'

cru_arr = []
eta_arr = []
eta_proj = []

log.basicConfig(level=log.INFO)


@get_eta_data("map_config.ini", 1961, 1990)
def get_eta(config, out_dict, data):
    global eta_arr
    eta_arr.append((config, out_dict, data))


@get_eta_data("map_config.ini", 2021, 2050)
def get_proj(config, out_dict, data):
    global eta_proj
    eta_proj.append((config, out_dict, data))

@get_cru_data("map_config.ini", 1961, 1990)
def get_cru(cru_conf, cru_dict, cru_data):
    global cru_arr
    cru_arr.append((cru_conf, cru_dict, cru_data))


@get_cru_data("line_config.ini", 1961, 1990)
def get_cru_line(cru_conf, cru_dict, cru_data):
    global cru_arr
    cru_arr.append((cru_conf, cru_dict, cru_data))


@get_eta_data_month("line_config.ini", 1961, 1990)
def get_eta_month(config, out_dict, data):
    global eta_arr
    eta_arr.append((config, out_dict, data))


def draw_anomalias():
    global cru_arr, eta_arr
    get_eta()
    get_cru()

    for eta_out, cru_out in zip(eta_arr, cru_arr):
        togrd = eta_out[2].getGrid()
        frgrd = cru_out[2].getGrid()
        grdfunc = Regridder(frgrd, togrd)
        avg = None
        if len(eta_out[2].shape) > 2:
            data1 = np.average(eta_out[2], axis=0)
        else:
            data1 = eta_out[2]

        if len(cru_out[2]) > 2:
            data2 = np.average(grdfunc(cru_out[2]), axis=0)
        else:
            data2 = grdfunc(cru_out[2])
        avg = data1 - data2
        data = eta_out[2]
        print avg.min(), avg.max()
        config, out_dict = eta_out[:2]
        var_name = out_dict['var'].upper()
        print var_name
        out_tmpl = config.get("COMMON", 'out_tmpl', True)
        print data.shape
        items = dict(config.items(var_name))
        # items["title"] = "%s vs %s - %s" % (eta_out[1]["model"].upper(), cru_out[1]["model"].upper(), items["title"])
        if var_name in ("PREC", "PRE"):
            items["level_min"], items["level_max"], items["level_int"] = -8*365, 8*365, 17
            data *= 365
            avg *= 365
        else:
            items["level_min"], items["level_max"], items["level_int"] = -10, 10, 21
        items["subtitle"] = "%s - %s: %s anual (1961 - 1990)" % (eta_out[1]["model"].upper(),
                                                                 cru_out[1]["model"].upper(),
                                                                 items["title"].decode("utf-8"))
        mymap = MPLMap(var_name, BOUNDS, **items)
        if var_name in ("PREC", "PRE"):
            mymap.levels = [-2600, -2200, -1800, -1400, -1000, -800, -600, -400, -200] + \
                           [0, 200, 400, 600, 800, 1000, 1400, 1800, 2200, 2600]
        mymap.set_title(items["subtitle"])
        out_dict["model"] = eta_out[1]["model"] + cru_out[1]["model"].upper()
        out_dict["escenario"] = "_anomalia"
        mymap.add_contour(data.getLongitude(), data.getLatitude(),
                          avg if avg is not None else data, items["unit"].decode("utf-8"), alt=True)
        mymap.add_shape("tarija", pth.join(SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84"), "UNIDADES", linewidth=0.7)
        mymap.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))


def compara_meses(shape_file, key, pos=1, title=""):
    global cru_arr, eta_arr
    mascaras = None
    if len(cru_arr) == 0 and len(eta_arr) == 0:
        get_eta()
        #get_eta_month()
        get_cru_line()

    tables = []

    for eta_out, cru_out in zip(eta_arr, cru_arr):
        print eta_out[1]["var"], cru_out[1]["var"]
        togrd = eta_out[2].getGrid()
        frgrd = cru_out[2].getGrid()
        grdfunc = Regridder(frgrd, togrd)
        config, out_dict, data = eta_out
        var_name = out_dict['var'].upper()
        out_tmpl = config.get("COMMON", 'out_tmpl', True)
        out_dict = dict(out_dict.iteritems())
        out_dict["model"] = eta_out[1]["model"] + cru_out[1]["model"].upper()
        items = dict(config.items(var_name))
        mult = 1
        if var_name in ("PREC", "PRE"):
            items["level_max"] = 12*30
            items["unit"] = "mm"
            mult = 30
        else:
            items["level_min"] = 8
            items["level_max"] = 28
        myline = MonthLineGraph(var_name, **items)
        if mascaras is None:
            mascaras = ShapeMask(shape_file, key,
                                 data.getLongitude()[:], data.getLatitude()[:], 0.1, False)
        table_data = pd.DataFrame(index=[nombre.split(":")[1] for nombre in mascaras.keys()],
                                  columns=calendar.month_name[1:13])
        for key in mascaras.keys():
            mask = mascaras[key]
            clave, nombre = key.split(":")
            clave = clave.split(".")[pos]
            myline.set_title("%s - %s" % (title, nombre))
            avg_data1 = []
            avg_data2 = []
            for idx, year in enumerate(range(1, 13)):
                masked_data = np.ma.array(eta_out[2][idx], mask=mask)
                avg_data1.append(masked_data.mean()*mult)
                masked_data = np.ma.array(grdfunc(cru_out[2][idx]), mask=mask)
                avg_data2.append(masked_data.mean()*mult)

            out_dict["period"] = "ene_dic"
            print key, var_name
            out_dict["region"] = clave
            table_data.loc[nombre, :] = avg_data2
            myline.add_line(avg_data1, 'r')
            myline.add_bar(avg_data2, 'b')
            myline.add_legend(("ETA", "CRU"), 0.5)
            out_dict["escenario"] = ""
            #myline.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))
            #myline.clear()
        tables.append(table_data)
    with pd.ExcelWriter(pth.join(OUTPUT_DIR, "anual_muni_cru.xlsx")) as writer:
        tables[0].to_excel(writer, sheet_name="Datos CRU PREC")
        tables[1].to_excel(writer, sheet_name="Datos CRU TEMP")


def draw_proj_anomalias():
    global eta_arr, eta_proj
    get_proj()
    get_eta()

    for p in [2021, 2031, 2041]:
        pf = p + 9
        idxi, idxf = p - 2021, p - 2021 + 9
        for proj_out, eta_out in zip(eta_proj, eta_arr):
            avg = None
            if len(proj_out[2].shape) > 2:
                data1 = np.average(proj_out[2][idxi:idxf], axis=0)
            else:
                data1 = proj_out[2]

            if len(eta_out[2]) > 2:
                data2 = np.average(eta_out[2], axis=0)
            else:
                data2 = eta_out[2]
            avg = data1 - data2
            data = proj_out[2]
            print avg.min(), avg.max()
            config, out_dict = proj_out[0], dict(proj_out[1].iteritems())
            var_name = out_dict['var'].upper()
            print var_name
            out_tmpl = config.get("COMMON", 'out_tmpl', True)
            print data.shape
            items = dict(config.items(var_name))
            #items["title"] = "Anomalia de la %s" % (items["title"])
            items["subtitle"] = "Anomalia de la %s anual (%d - %d)" % (items["title"].decode("utf-8"),
                                                                        p, pf)
            out_dict["period"] = "%d_%d" % (p, pf)
            out_dict["step"] = 10
            if var_name in ("PREC", "PRE"):
                items["level_min"], items["level_max"], items["level_int"] = -8*365, 8*365, 17
                data *= 365
                avg *= 365
            else:
                items["level_min"], items["level_max"], items["level_int"] = -10, 10, 21
            mymap = MPLMap(var_name, BOUNDS, **items)
            if var_name in ("PREC", "PRE"):  # bad design
                mymap.levels = [-2600, -2200, -1800, -1400, -1000, -800, -600, -400, -200] + \
                               [0, 200, 400, 600, 800, 1000, 1400, 1800, 2200, 2600]
            mymap.set_title(items["subtitle"])
            out_dict["model"] = proj_out[1]["model"]
            out_dict["escenario"] += "_anomalia"
            mymap.add_contour(data.getLongitude(), data.getLatitude(),
                              avg if avg is not None else data, items["unit"].decode("utf-8"), alt=True)
            mymap.add_shape("tarija", pth.join(SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84"), "UNIDADES", linewidth=0.7)
            mymap.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))


if __name__ == "__main__":
    #draw_anomalias()
    #draw_proj_anomalias()
    #compara_meses(pth.join(SHP_DIR, "shp", "tarija_region.shp"), "%(HASC_2)s:%(NAME_0)s - %(NAME_1)s")
    #compara_meses(pth.join(SHP_DIR, "shp", "tarija.shp"), "%(HASC_2)s:%(NAME_1)s - %(NAME_2)s", 2)
    compara_meses(pth.join(SHP_DIR, "shp", "tarija_muni.shp"), "MUN_%(CODIGO)s:%(NOM_MUN)s", 0, "Municipio")
    #compara_meses(pth.join(SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84.shp"),
    #              "SDV_%(COD_SDV)s:%(UNIDADES)s", 0, "Sistema de Vida")