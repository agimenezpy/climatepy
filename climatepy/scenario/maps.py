import ConfigParser as cfgParser
import logging as log
import numpy as np
import os.path as pth
from regrid2 import Regridder

from climatepy.figures import MPLMap
from climatepy.scenario.data import get_data

__author__ = 'agimenez'


def get_grid(data_file, extent, year_ini, year_end):
    out_dict, data = get_data(data_file, extent, year_ini, year_end)
    return data.getGrid()


def draw_base(filename, data_file, extent, year_ini, year_end,
              shape_file, shape_title, out_dir, to_grid=None):
    config = cfgParser.ConfigParser()
    config.read(filename)
    out_dict, data = get_data(data_file, extent, year_ini, year_end)
    log.debug("Data shape %s", data.shape)
    if to_grid is not None:
        frgrd = data.getGrid()
        grdfunc = Regridder(frgrd, get_grid(to_grid, extent, year_ini, year_end))
        data = grdfunc(data)

    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    # to mm/year
    if var_name.startswith("PRE"):
        data *= 12
    if len(data.shape) > 2:
        avg = np.average(data, axis=0)
    else:
        avg = data
    log.debug("Promedios %s %f %f", var_name, avg.min(), avg.max())
    out_dict["escenario"] = "_base"

    items = dict(config.items(var_name))
    items["title"] = "%s - %s" % (out_dict["model"].upper(), items["title"])
    items["subtitle"] = "%s anual (1961 - 1990)" % (unicode(items["title"], "utf-8"))

    mymap = MPLMap(var_name, extent, **items)
    mymap.set_title(items["subtitle"])

    if var_name.startswith("PRE"):
        mymap.levels = [0, 200, 400, 600, 800, 1000, 1400, 2200, 2600]
    mymap.add_contour(data.getLongitude(), data.getLatitude(),
                      avg,
                      items["unit"].decode("utf-8"))
    shape_file, ext = pth.splitext(shape_file)
    shape_name = pth.basename(shape_file)
    mymap.add_shape(shape_name, shape_file, shape_title,
                    linewidth=0.7, color="#444444")
    mymap.draw(pth.join(out_dir, out_tmpl % out_dict))


def draw_steps_years(filename, data_file, extent, year_ini, year_end,
                     shape_file, shape_title, out_dir, steps=5):
    config = cfgParser.ConfigParser()
    config.read(filename)
    out_dict, data = get_data(data_file, extent, year_ini, year_end)
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    log.debug("Data shape %s", data.shape)
    items = dict(config.items(var_name))
    #items["title"] = "%s %s - %s" % (out_dict["model"].upper(),
    #                                 out_dict["escenario"],
    #                                 items["title"])
    times = data.getTime().asComponentTime()
    yi, ye = times[0].year, times[-1].year
    out_dict["step"] = steps

    # to mm/year
    if var_name.startswith("PRE"):
        data *= 12

    mymap = MPLMap(var_name, extent, **items)
    if var_name.startswith("PRE"):
        mymap.levels = [0, 200, 400, 600, 800, 1000, 1400, 2200, 2600]

    for idx, year in enumerate(xrange(yi, ye, steps)):
        mymap.set_title("%s %s: %s anual (%d - %d)" % (out_dict["model"].upper(),
                                                       out_dict["escenario"],
                                                       items["title"].decode("utf-8"),
                                                       year, year + steps - 1))
        out_dict["period"] = "%d_%d" % (year, year + steps - 1)
        idxs, idxe = idx*steps, idx*steps + steps
        avg = np.average(data[idxs:idxe, :, :], axis=0)
        log.debug("%s: %f %f %d %d", out_dict["period"],
                  avg.min(), avg.max(), idxs, idxe)
        mymap.add_contour(data.getLongitude(), data.getLatitude(),
                          avg, items["unit"].decode("utf-8"))
        shape_file, ext = pth.splitext(shape_file)
        shape_name = pth.basename(shape_file)
        mymap.add_shape(shape_name, shape_file, shape_title, linewidth=0.7, color="#444444")
        mymap.draw(pth.join(out_dir, out_tmpl % out_dict))
        mymap.clear()


def draw_compare_base(filename, cru_file, eta_file, extent, year_ini, year_end,
                      shape_file, shape_title, out_dir):
    config = cfgParser.ConfigParser()
    config.read(filename)
    out_dict, eta_out = get_data(eta_file, extent, year_ini, year_end)
    cru_dict, cru_out = get_data(cru_file, extent, year_ini, year_end)
    togrd = eta_out.getGrid()
    frgrd = cru_out.getGrid()
    grdfunc = Regridder(frgrd, togrd)
    if len(eta_out.shape) > 2:
        data1 = np.average(eta_out, axis=0)
    else:
        data1 = eta_out

    if len(cru_out) > 2:
        data2 = np.average(grdfunc(cru_out), axis=0)
    else:
        data2 = grdfunc(cru_out)
    data = eta_out
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    items = dict(config.items(var_name))
    levels = None
    if var_name.startswith("PRE"):

        levels = [-800, -600, -400, -200] + \
                 [0, 200, 400, 600, 800]
        data1 *= 12
        data2 *= 12
    else:
        items["level_min"], items["level_max"], items["level_int"] = -5, 5, 11
    items["subtitle"] = "%s - %s: %s anual (1961 - 1990)" % (out_dict["model"].upper(),
                                                             cru_dict["model"].upper(),
                                                             items["title"].decode("utf-8"))
    mymap = MPLMap(var_name, extent, **items)
    if levels is not None:
        mymap.levels = levels

    avg = data1 - data2
    log.debug("%s Max and min %f %f", data.shape, avg.min(), avg.max())
    mymap.set_title(items["subtitle"])
    out_dict["model"] = out_dict["model"] + cru_dict["model"].upper()
    out_dict["escenario"] = "_anomalia"
    mymap.add_contour(data.getLongitude(), data.getLatitude(),
                      avg, items["unit"].decode("utf-8"), alt=True)
    shape_file, ext = pth.splitext(shape_file)
    shape_name = pth.basename(shape_file)
    mymap.add_shape(shape_name, shape_file, shape_title,
                    linewidth=0.7, color="#444444")
    mymap.draw(pth.join(out_dir, out_tmpl % out_dict))


def draw_proj_anomalia(filename, proj_file, extent, year_ini, year_end,
                       shape_file, shape_title, out_dir, steps=10):
    config = cfgParser.ConfigParser()
    config.read(filename)
    out_dict, eta_out = get_data(proj_file, extent, 1961, 1990)
    proj_dict, proj_out = get_data(proj_file, extent, year_ini, year_end)

    out_dict["escenario"] += "_anomalia"
    var_name = out_dict['var'].upper()
    out_tmpl = config.get("COMMON", 'out_tmpl', True)
    times = proj_out.getTime().asComponentTime()
    yi, ye = times[0].year, times[-1].year
    items = dict(config.items(var_name))
    out_dict["step"] = steps

    if len(eta_out.shape) > 2:
        data2 = np.average(eta_out, axis=0)
    else:
        data2 = eta_out

    data = proj_out
    for idx, year in enumerate(xrange(yi, ye, steps)):
        idxs, idxe = idx * steps, idx * steps + steps
        data1 = np.average(data[idxs:idxe, :, :], axis=0)
        avg = data1 - data2
        levels = None
        if var_name.startswith("PRE"):
            levels = [-800, -600, -400, -200] + \
                     [0, 200, 400, 600, 800]
            avg *= 12
        else:
            items["level_min"], items["level_max"], items["level_int"] = -7, 7, 15
        log.debug("%s Max and min %f %f", data1.shape, avg.min(), avg.max())
        items["subtitle"] = "Anomalia de la %s anual (%d - %d)" % (items["title"].decode("utf-8"),
                                                                   year, year + steps - 1)
        out_dict["period"] = "%d_%d" % (year, year + steps - 1)

        mymap = MPLMap(var_name, extent, **items)
        if levels is not None:
            mymap.levels = levels

        mymap.set_title(items["subtitle"])
        mymap.add_contour(data.getLongitude(), data.getLatitude(),
                          avg, items["unit"].decode("utf-8"), alt=True)
        shape_file, ext = pth.splitext(shape_file)
        shape_name = pth.basename(shape_file)
        mymap.add_shape(shape_name, shape_file, shape_title,
                        linewidth=0.7, color="#444444")
        mymap.draw(pth.join(out_dir, out_tmpl % out_dict))
