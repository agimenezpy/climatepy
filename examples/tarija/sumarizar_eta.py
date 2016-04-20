__author__ = 'agimenez'
import os
import glob
from proceso import ROOT_DIR, ETA_10K
from climatepy.grads.ops import avg_data
from climatepy.grads.files import CtlConfig, CtlVar, CtlFile
import logging as log
from sys import argv, exit
import re
import datetime
import copy
import itertools

config_10km = CtlConfig()
prec_var = CtlVar()
temp_var = CtlVar()
tmin_var = CtlVar()
tmax_var = CtlVar()
config_20km = CtlConfig()
DATE_FORMAT = "([0-9]{4})([0-9]{2})([0-9]{2})"
NUM_THREADS = 4
LOG_FORMAT = "%(levelname)s:%(thread)d - %(threadName)s:%(asctime)-15s %(message)s"
YEARS = (1961, 2040)


def init_config():
    global config_10km
    global prec_var, temp_var, tmin_var, tmax_var
    config_10km.grid_x = 330
    config_10km.grid_y = 270
    config_10km.grid_z = 1
    config_10km.times = 1
    config_10km.lon = -73
    config_10km.lat = -39
    config_10km.template = True

    prec_var.name = "PREC"
    prec_var.low = 0
    prec_var.high = 99
    prec_var.desc = "Total   3h Precip."
    prec_var.unit = "(m)"

    temp_var.name = "TP2M"
    tmin_var.name = "MNTP"
    tmax_var.name = "MXTP"
    temp_var.low = tmin_var.low = tmax_var.low = 0
    temp_var.high = tmin_var.high = tmax_var.high = 99
    temp_var.unit = tmin_var.unit = tmax_var.unit = "(K)"
    temp_var.desc = "Shelter Temperature"
    tmin_var.desc = "Min Temperature"
    tmax_var.desc = "Max Temperature"

    log.basicConfig(level=log.INFO, format=LOG_FORMAT)


def get_normal_date(basename):
    tuple_date = re.search(DATE_FORMAT, basename).groups()
    year, month, day = map(int, tuple_date)
    return datetime.datetime(year, month, day).strftime("%d%b%Y")


def dump_file(files, out_dir, alt_name, var_n, config):
    file_name = os.path.basename(files[0])
    out_name = os.path.splitext(file_name)[0]
    if alt_name:
        out_name = out_name.replace(*alt_name.split("|"))
    config.date_init = get_normal_date(out_name)
    out = os.path.join(out_dir, out_name + ".bin")
    avg_data(files, out, config.grid_y, config.grid_x, var_n, 1, config)


def dump_template(file_base, out_dir, alt_name, config):
    file_name = os.path.basename(file_base)
    out_name = os.path.splitext(file_name)[0]
    if alt_name:
        out_name = out_name.replace(*alt_name.split("|"))
    tmpl_name = re.sub(DATE_FORMAT, "template", out_name)
    bin_name = re.sub(DATE_FORMAT, "%y4%m2%d2", out_name) + ".bin"
    out = os.path.join(out_dir, tmpl_name + ".bin")
    ctlfile = CtlFile(out)
    config.options = ["TEMPLATE"]
    values = config.to_dict()
    values["filename"] = bin_name
    ctlfile.save(**values)

# Esto esta mal definido
def multiprocesor(func):
    def calc_mp(year_ini=1961, year_end=2005):
        from threading import Thread
        thread_childs = []
        thread_id = 0
        years = range(year_ini, year_end, 10)
        root_dir = "%d_%d" % (year_ini, year_end)
        for year in years:
            yi = year
            if year + 10 < year_end:
                ye = (year + 10) % year_end - 1
            else:
                ye = (year + 10) - (year + 10) % year_end

            if len(thread_childs) == NUM_THREADS:
                cur_thread = thread_childs.pop(0)
                log.info("Esperando al Thread %s " % cur_thread.name)
                cur_thread.join()

            name = "Thread #%d:%d,%d" % (thread_id, yi, ye)
            log.info("Lanzando nuevo " + name)
            cur_thread = Thread(None, func, name,
                                [yi, ye], {"DIR": root_dir, "MKTMPL": year == YEARS[0]})
            cur_thread.start()
            thread_childs.append(cur_thread)
            thread_id += 1

        while len(thread_childs) > 0:
            cur_thread = thread_childs.pop(0)
            if cur_thread.is_alive():
                cur_thread.join()

    return calc_mp

@multiprocesor
def mensual_10km(year_ini=1961, year_end=2005, **kwargs):
    root_dir = "%d_%d" % (year_ini, year_end)
    mk_tmpl = True
    if kwargs:
        root_dir = kwargs.get("DIR", root_dir)
        mk_tmpl = kwargs.get("MKTMPL", False)

    years = range(year_ini, year_end+1)
    months = range(1, 13)
    for cur_var in ("Prec", "Temp"):
        my_config = copy.copy(config_10km)
        if cur_var == "Prec":
            my_config.vars = [prec_var]
            my_config.title = "Precipitacion"
        else:
            my_config.vars = [temp_var, tmax_var, tmin_var]
            my_config.title = "Temperatura"
        my_config.date_steps = "1mo"

        for year, month in itertools.product(years, months):
            files = glob.glob(os.path.join(ETA_10K,
                                           "%s/Diario/%s/*_%d%02d*.bin" %
                                           (root_dir, cur_var, year, month)))
            out_dir = os.path.join(ETA_10K, "Mensual/%s/" % cur_var)
            dump_file(files, out_dir, "Diaria|Mensual", len(my_config.vars), my_config)

        if my_config.template and mk_tmpl:
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)*12
            dump_template(files[0], out_dir, "Diaria|Mensual", my_config)

@multiprocesor
def anual_10km(year_ini=1961, year_end=2005, **kwargs):
    mk_tmpl = True
    if kwargs:
        mk_tmpl = kwargs.get("MKTMPL", False)

    for cur_var in ("Prec", "Temp"):
        my_config = copy.copy(config_10km)
        my_config.date_steps = "1yr"
        if cur_var == "Prec":
            my_config.vars = [prec_var]
            my_config.title = "Precipitacion"
        else:
            my_config.vars = [temp_var, tmax_var, tmin_var]
            my_config.title = "Temperatura"

        years = range(year_ini, year_end+1)
        for year in years:
            files = glob.glob(os.path.join(ETA_10K,
                                           "Mensual/%s/*_%d*01.bin" % (cur_var, year)))
            out_dir = os.path.join(ETA_10K, "Anual/%s/" % cur_var)
            dump_file(files, out_dir, "Mensual|Anual", len(my_config.vars), my_config)

        if my_config.template and mk_tmpl:
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)
            dump_template(files[0], out_dir, "Mensual|Anual", my_config)

"""Run configurations

A. Generar Mensual/*
====================
1) sumarizar_eta.py mensual_10km 1961,2005
2) sumarizar_eta.py mensual_10km 2006,2040
3) sumarizar_eta.py mensual_10km 2041,2070

B. Generar Anual/*
1) sumarizar_eta.py mensual_10km 1961,2070
"""
if __name__ == '__main__':
    if len(argv) > 1:
        my_module = locals()
        init_config()
        for idx, func in enumerate(argv[1:]):
            if my_module.get(func, False):
                func_obj = my_module[func]
                args = []
                try:
                    yi, yf = argv[(idx+1)+1].split(",")
                    args.extend([int(yi), int(yf)])
                except:
                    pass
                func_obj(*args)
    else:
        print "Usage: ..."
        exit(1)