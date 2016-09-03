import ConfigParser as cfgParser
import logging as log
import os
import sys
from glob import glob
from os import path as pth

from climatepy.data import Dataset
from climatepy.scenario import REMOTE_URL

__author__ = 'agimenez'


def get_remote_file(filename):
    return REMOTE_URL + "escenarios/ETA/" + ("/".join(filename.split(os.sep)[-4:]))


def get_data(filename, extent, year_ini, year_end, yearly=True):
    bound_lat = (extent[0][1], extent[1][1])
    bound_lon = (extent[0][0], extent[1][0])
    out_dict = {"sep": os.sep,
                "period": "%d_%d" % (year_ini, year_end),
                "step": (year_end - year_ini + 1)}
    if filename.find("RCP8.5") > 0:
        out_dict["model"], _, _, out_dict["escenario"] = \
            pth.basename(filename).split("_")[0:4]
        out_dict["escenario"] = out_dict["escenario"].replace(".", "")
    else:
        out_dict["model"], _, out_dict["escenario"] = \
            pth.basename(filename).split("_")[0:3]
    with Dataset(filename) as data_set:
        varname = filter(lambda v: v in ('prec', 'tp2m', 'tmp', 'pre'),
                         data_set.listvariables())[0]
        if yearly:
            data = data_set(varname, squeeze=1,
                            time=("%d-01-01" % year_ini,
                                  "%d-12-01" % year_end),
                            latitude=bound_lat, longitude=bound_lon)

        else:
            last_data = None
            for year in range(year_ini, year_end+1):
                log.info("Obteniendo year %s-%d", varname, year)
                data = data_set(varname, squeeze=1,
                                time=("%d-01-01" % year,
                                      "%d-12-01" % year),
                                latitude=bound_lat,
                                longitude=bound_lon)
                if last_data is None:
                    last_data = data
                else:
                    last_data = data + last_data
            if varname not in ("prec", "pre"):
                last_data /= (1.*(year_end - year_ini + 1))  # Average instead of accumulation

    out_dict['var'] = varname
    return out_dict, data


def get_eta_data(root_dir, extent, filename, year_ini, year_end, remote=False):
    files = [
        pth.join(root_dir,
                 "Anual/Prec/Eta_HG2ES_RCP45_20km_Prec_Anual_template.ctl"),
        pth.join(root_dir,
                 "Anual/Temp/Eta_HG2ES_RCP45_20km_Temp_Anual_template.ctl")
    ]

    if sys.platform == "win32":
        remote = True
        files = ["/escenarios/ETA/" + ("/".join(fname.split(os.sep)[-4:]))
                 for fname in files]

    return get_data_wrapper(filename, extent, year_ini, year_end, files, remote=remote)


def get_eta_data_month(root_dir, extent, filename, year_ini, year_end,
                       remote=False):
    files = glob(pth.join(root_dir, "Mensual", "*", "Eta*_template.ctl"))
    if sys.platform == "win32":
        remote = True
        files = ["/escenarios/ETA/" + ("/".join(fname.split(os.sep)[-4:]))
                 for fname in files]

    return get_data_wrapper(filename, extent, year_ini, year_end, files,
                            yearly=False, remote=remote)


def get_cru_data(extent, filename, year_ini, year_end):
    files = ["cru/" + fname for fname in ("cru_pre_clim_1961-1990.nc",
                                          "cru_tmp_clim_1961-1990.nc")]
    bound_lat = (extent[0][1], extent[1][1])
    bound_lon = (extent[0][0], extent[1][0])
    extent = ((bound_lon[0] - 0.25, bound_lon[1] + 0.25),
              (bound_lat[0] - 0.25, bound_lat[1] + 0.25))

    return get_data_wrapper(filename, extent, year_ini, year_end, files,
                            remote=True)


def get_data_wrapper(filename, extent, year_ini, year_end, files, yearly=True, remote=False):
    def wrapper(fnc):
        def wrap_args(*args):
            config = cfgParser.ConfigParser()
            config.read(filename)
            out_dict = {}
            for data_file in files:
                if remote:
                    url_file = REMOTE_URL + data_file
                else:
                    url_file = data_file
                out_dict["var"], data = get_data(url_file, extent, year_ini,
                                                 year_end, yearly)
                log.debug("Opening file %s", url_file)

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
