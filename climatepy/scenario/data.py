import os
from glob import glob
from os import path as pth
from climatepy.scenario import REMOTE_URL
from climatepy.data import Dataset
import ConfigParser as cfgParser
import logging as log

__author__ = 'agimenez'

def get_remote_file(filename):
    return REMOTE_URL + "escenarios/ETA/" + ("/".join(filename.split(os.sep)[-4:]))


def get_eta_data(root_dir, filename, year_ini, year_end):
    files = ["/escenarios/ETA/" + ("/".join(fname.split(os.sep)[-4:]))
             for fname in glob(pth.join(root_dir, "Anual", "*",
                                        "Eta*_template.ctl"))]

    return get_data(filename, year_ini, year_end, files)


def get_eta_data_month(root_dir, filename, year_ini, year_end):
    files = ["/escenarios/ETA/" + ("/".join(fname.split(os.sep)[-4:]))
             for fname in glob(pth.join(root_dir, "Mensual", "*",
                                        "Eta*_template.ctl"))]

    return get_data(filename, year_ini, year_end, files, False)


def get_cru_data(filename, extent, year_ini, year_end):
    files = ["cru/" + fname for fname in ("cru_pre_clim_1961-1990.nc", "cru_tmp_clim_1961-1990.nc")]
    bound_lat = (extent[0][1], extent[1][1])
    bound_lon = (extent[0][0], extent[1][0])
    extent = ((bound_lon[0] - 0.25, bound_lon[1] + 0.25),
              (bound_lat[0] - 0.25, bound_lat[1] + 0.25))

    return get_data(filename, extent, year_ini, year_end, files)


def get_data(filename, extent, year_ini, year_end, files, yearly=True):
    def wrapper(fnc):
        def wrap_args(*args):
            bound_lat = (extent[0][1], extent[1][1])
            bound_lon = (extent[0][0], extent[1][0])
            config = cfgParser.ConfigParser()
            config.read(filename)
            for data_file in files:
                out_dict = {"sep": os.sep,
                            "period": "%d_%d" % (year_ini, year_end),
                            "step": (year_end - year_ini + 1)}
                out_dict["model"], __, out_dict["escenario"] = pth.basename(data_file).split("_")[0:3]
                url_file = REMOTE_URL + data_file
                with Dataset(url_file) as data_set:
                    out_dict["var"] = filter(lambda v: v in ('prec', 'tp2m', 'tmp', 'pre'),
                                             data_set.listvariables())[0]

                    if yearly:
                        data = data_set(out_dict["var"], squeeze=1,
                                        time=("%d-01-01" % year_ini,
                                              "%d-12-01" % year_end),
                                        latitude=bound_lat, longitude=bound_lon)

                    else:
                        last_data = None
                        for year in range(year_ini, year_end+1):
                            log.info("Obteniendo year %s-%d", out_dict["var"],
                                     year)
                            data = data_set(out_dict["var"], squeeze=1,
                                            time=("%d-01-01" % year,
                                                  "%d-12-01" % year),
                                            latitude=bound_lat,
                                            longitude=bound_lon)
                            if last_data is None:
                                last_data = data
                            else:
                                last_data = data + last_data
                        if out_dict["var"] not in ("prec", "pre"):
                            last_data /= (1.*(year_end - year_ini + 1))  # Average instead of accumulation

                    if out_dict["var"] == 'prec':
                        data *= 1000  # To mm/day
                    elif out_dict["var"] == 'pre':
                        data /= 30  # To mm/day
                    elif out_dict["var"] == 'tp2m':
                        data -= 273  # To Celsius
                    fnc(config, out_dict, data, *args)
        return wrap_args
    return wrapper

def with_config(filename, year_ini, year_end):
    def wrapper(fnc):
        def wrap_args(*args):
            config = cfgParser.ConfigParser()
            config.read(filename)
            out_dict = {"sep": os.sep, "period": "%d_%d" % (year_ini, year_end),
                        "step": (year_end - year_ini + 1)}
            fnc(config, out_dict, year_ini, year_end, *args)
        return wrap_args
    return wrapper
