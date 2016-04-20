from proceso import BOUNDS, SHP_DIR, OUTPUT_DIR, get_eta_data, get_cru_data
import os.path as pth
from climatepy.figures import MPLMap
import numpy as np
from regrid2 import Regridder

__author__ = 'agimenez'

togrid = None

@get_eta_data("map_config.ini", 1961, 1990)
def get_eta(config, out_dict, data):
    global togrid
    if togrid is None:
        togrid = data.getGrid()

@get_cru_data("map_config.ini", 1961, 1990)
def draw_cru_base(config, out_dict, data):
    if togrid is not None:
        frgrd = data.getGrid()
        grdfunc = Regridder(frgrd, togrid)
        data = grdfunc(data)
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    print data.shape
    items = dict(config.items(var_name))
    #items["title"] = "%s - %s" % (out_dict["model"].upper(), items["title"])
    items["subtitle"] = "%s anual (1961 - 1990)" % (unicode(items["title"], "utf-8"))
    mymap = MPLMap(var_name, BOUNDS, **items)
    mymap.set_title(items["subtitle"])
    if var_name == "PRE":
        data *= 365
        mymap.levels = [0, 200, 400, 600, 800, 1000, 1400, 1800, 2200, 2600, 3000, 3400, 3800, 4200]
    avg = None
    if len(data.shape) > 2:
        avg = np.average(data, axis=0)
        print avg.min(), avg.max()
    else:
        print data.min(), data.max()
    out_dict["escenario"] = "_base"
    mymap.add_contour(data.getLongitude(), data.getLatitude(),
                      avg if avg is not None else data, items["unit"].decode("utf-8"))
    mymap.add_shape("tarija", pth.join(SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84"), "UNIDADES", linewidth=0.7)
    #mymap.draw_points(pth.join(SHP_DIR, "shp", "tarija_muni"), "NOM_MUN", True, {"color": "#cccccc", "fontsize": 10})
    mymap.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))


@get_eta_data("map_config.ini", 1961, 1990)
def draw_base(config, out_dict, data):
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    print data.shape
    items = dict(config.items(var_name))
    #items["title"] = "%s - %s" % (out_dict["model"].upper(), items["title"])
    items["subtitle"] = "%s anual (1961 - 1990)" % (items["title"].decode("utf-8"))
    mymap = MPLMap(var_name, BOUNDS, **items)
    if var_name == "PREC":
        data *= 365
        mymap.levels = [0, 200, 400, 600, 800, 1000, 1400, 1800, 2200, 2600, 3000, 3400, 3800, 4200]
    mymap.set_title(items["subtitle"])
    avg = None
    if len(data.shape) > 2:
        avg = np.average(data, axis=0)
        print avg.min(), avg.max()
    else:
        print data.min(), data.max()
    out_dict["escenario"] = "_base"
    mymap.add_contour(data.getLongitude(), data.getLatitude(),
                      avg if avg is not None else data, items["unit"].decode("utf-8"))
    mymap.add_shape("tarija", pth.join(SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84"), "UNIDADES", linewidth=0.7)
    mymap.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))


@get_eta_data("map_config.ini", 2016, 2050)
def draw_five_years(config, out_dict, data):
    draw_steps_years(config, out_dict, data)


@get_eta_data("map_config.ini", 2021, 2050)
def draw_ten_years(config, out_dict, data):
    draw_steps_years(config, out_dict, data, 10)


def draw_steps_years(config, out_dict, data, steps=5):
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    print data.shape
    items = dict(config.items(var_name))
    #items["title"] = "%s %s - %s" % (out_dict["model"].upper(), out_dict["escenario"], items["title"])
    times = data.getTime().asComponentTime()
    yi, ye = times[0].year, times[-1].year
    mymap = MPLMap(var_name, BOUNDS, **items)
    out_dict["step"] = steps
    if var_name == "PREC":
        data *= 365
        mymap.levels = [0, 200, 400, 600, 800, 1000, 1400, 1800, 2200, 2600, 3000, 3400, 3800, 4200]
    for idx, year in enumerate(xrange(yi, ye, steps)):
        mymap.set_title("%s %s: %s anual (%d - %d)" % (out_dict["model"].upper(), out_dict["escenario"],
                                                           items["title"].decode("utf-8"),
                                                           year, year + steps - 1))
        out_dict["period"] = "%d_%d" % (year, year + steps - 1)
        #idxs, idxe = year - yi, year - yi + steps
        idxs, idxe = idx*steps, idx*steps + steps
        avg = np.average(data[idxs:idxe, :, :], axis=0)
        print out_dict["period"], avg.min(), avg.max(), idxs, idxe
        mymap.add_contour(data.getLongitude(), data.getLatitude(),
                          avg, items["unit"].decode("utf-8"))
        mymap.add_shape("tarija", pth.join(SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84"), "UNIDADES", linewidth=0.7)
        mymap.draw(pth.join(OUTPUT_DIR, out_tmpl % out_dict))
        mymap.clear()

if __name__ == '__main__':
    #
    #draw_five_years()
    draw_ten_years()
    #draw_base()
    #get_eta()
    #draw_cru_base()