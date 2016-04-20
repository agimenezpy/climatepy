__author__ = 'agimenez'
import os.path as pth
import ConfigParser as cfgParser
from glob import glob
import os
from climatepy.data import Dataset

ROOT_DIR = pth.dirname(pth.dirname(pth.dirname(__file__))) #"/Users/agimenez/Desktop/ProyectoCC/"
REMOTE_URL = "http://dap.pykoder.com/"
ETA_10K = pth.join(ROOT_DIR, "escenarios", "ETA", "Eta_10km")
ETA_20K = pth.join(ROOT_DIR, "escenarios", "ETA", "Eta_20km")
SHP_DIR = pth.join(ROOT_DIR, "tarija", "alcance")
OUTPUT_DIR = pth.join(ROOT_DIR, "tarija", "salida")
LOG_FORMAT = "%(levelname)s:%(thread)d-%(threadName)s:%(asctime)-15s %(message)s"
BOUNDS_GRAL = ((-67.5, -23.5), (-61.5, -18.5))
BOUNDS = ((-65.5, -23.5), (-61.5, -20.5))
BOUND_LAT = (BOUNDS[0][1], BOUNDS[1][1])
BOUND_LON = (BOUNDS[0][0], BOUNDS[1][0])


def get_remote_file(filename):
    return REMOTE_URL + "escenarios/ETA/" + ("/".join(filename.split(os.sep)[-4:]))


def get_eta_data(filename, year_ini, year_end):
    files = ["/escenarios/ETA/" + ("/".join(fname.split(os.sep)[-4:]))
             for fname in glob(pth.join(ETA_10K, "Anual", "*", "Eta*_template.ctl"))]

    return get_data(filename, year_ini, year_end, files)


def get_eta_data_month(filename, year_ini, year_end):
    files = ["/escenarios/ETA/" + ("/".join(fname.split(os.sep)[-4:]))
             for fname in glob(pth.join(ETA_10K, "Mensual", "*", "Eta*_template.ctl"))]

    return get_data(filename, year_ini, year_end, files, False)


def get_cru_data(filename, year_ini, year_end):
    files = ["cru/" + fname for fname in ("cru_pre_clim_1961-1990.nc", "cru_tmp_clim_1961-1990.nc")]
    global BOUND_LAT, BOUND_LON
    BOUND_LAT = (BOUND_LAT[0] - 0.25, BOUND_LAT[1] + 0.25)
    BOUND_LON = (BOUND_LON[0] - 0.25, BOUND_LON[1] + 0.25)

    return get_data(filename, year_ini, year_end, files)


def get_data(filename, year_ini, year_end, files, yearly=True):
    def wrapper(fnc):
        def wrap_args(*args):
            config = cfgParser.ConfigParser()
            config.read(filename)
            for data_file in files:
                out_dict = {"sep": os.sep, "period": "%d_%d" % (year_ini, year_end), "step": (year_end - year_ini + 1)}
                out_dict["model"], __, out_dict["escenario"] = pth.basename(data_file).split("_")[0:3]
                url_file = REMOTE_URL + data_file
                with Dataset(url_file) as data_set:
                    out_dict["var"] = filter(lambda v: v in ('prec', 'tp2m', 'tmp', 'pre'), data_set.listvariables())[0]

                    if yearly:
                        data = data_set(out_dict["var"], squeeze=1, time=("%d-01-01" % year_ini, "%d-12-01" % year_end),
                                        latitude=BOUND_LAT, longitude=BOUND_LON)

                    else:
                        last_data = None
                        for year in range(year_ini, year_end+1):
                            print "Obteniendo year %s-%d" % (out_dict["var"], year)
                            data = data_set(out_dict["var"], squeeze=1, time=("%d-01-01" % year, "%d-12-01" % year),
                                            latitude=BOUND_LAT, longitude=BOUND_LON)
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
            out_dict = {"sep": os.sep, "period": "%d_%d" % (year_ini, year_end), "step": (year_end - year_ini + 1)}
            fnc(config, out_dict, year_ini, year_end, *args)
        return wrap_args
    return wrapper