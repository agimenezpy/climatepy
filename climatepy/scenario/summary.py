import os
import glob
from climatepy.scenario import LOG_FORMAT, DATE_FORMAT, NUM_THREADS, ETA_20K
from climatepy.scenario.config import (YEARS, config_20km, prec_var,
                                       temp_var, tmin_var, tmax_var)
from climatepy.grads.ops import avg_data, sum_data, CtlFile
import logging as log
from sys import argv, exit
import re
import datetime
import copy
import itertools

log.basicConfig(level=log.INFO, format=LOG_FORMAT)

__author__ = 'agimenez'

def get_normal_date(basename):
    tuple_date = re.search(DATE_FORMAT, basename).groups()
    year, month, day = map(int, tuple_date)
    return datetime.datetime(year, month, day).strftime("%d%b%Y")


def dump_file(var_name, files, out_dir, alt_name, var_n, config):
    file_name = os.path.basename(files[0])
    out_name = os.path.splitext(file_name)[0]
    if alt_name:
        out_name = out_name.replace(*alt_name.split("|"))
    config.date_init = get_normal_date(out_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out = os.path.join(out_dir, out_name + ".bin")
    if var_name == "Prec":
        sum_data(files, out, config.grid_y, config.grid_x, var_n, 1, config)
    else:
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

def multiprocesor(func):
    def calc_mp(in_dir, out_dir, year_ini=1961, year_end=2005):
        from threading import Thread
        thread_childs = []
        thread_id = 0
        years = range(year_ini, year_end, 10)
        for year in years:
            yi = year
            if year + 10 < year_end:
                ye = (year + 10) % year_end - 1
            else:
                ye = (year + 10) - (year + 10) % year_end

            if len(thread_childs) == NUM_THREADS:
                cur_thread = thread_childs.pop(0)
                log.info("Esperando al Thread %s ", cur_thread.name)
                cur_thread.join()

            name = "Thread #%d:%d,%d" % (thread_id, yi, ye)
            log.info("Lanzando nuevo %s", name)
            cur_thread = Thread(None, func, name, [in_dir, out_dir, yi, ye], {
                "MKTMPL": year == YEARS[0]
            })
            cur_thread.start()
            thread_childs.append(cur_thread)
            thread_id += 1

        while len(thread_childs) > 0:
            cur_thread = thread_childs.pop(0)
            if cur_thread.is_alive():
                cur_thread.join()

    return calc_mp

@multiprocesor
def montly(in_dir, out_dir, year_ini=1961, year_end=2005, **kwargs):
    kwargs = kwargs or {}
    mk_tmpl = kwargs.get("MKTMPL", False)

    years = range(year_ini, year_end+1)
    months = range(1, 13)
    root_dir = ""
    if 1961 <= year_ini <= 2005:
        root_dir = "1961_2005"
    elif 2006 <= year_ini <= 2040:
        root_dir = "2006_2040"
    elif 2040 <= year_ini <= 2070:
        root_dir = "2040_2070"
    for cur_var in ("Prec", "Temp"):
        my_config = copy.copy(config_20km)
        if cur_var == "Prec":
            my_config.vars = [prec_var]
            my_config.title = "Precipitacion"
        else:
            my_config.vars = [temp_var, tmax_var, tmin_var]
            my_config.title = "Temperatura"
        my_config.date_steps = "1mo"

        out_path = os.path.join(out_dir, "Mensual", cur_var)
        last_file = None
        for year, month in itertools.product(years, months):
            files = sorted(glob.glob(os.path.join(in_dir,
                                           "%s/Diario/%s/*_%d%02d*.bin" %
                                           (root_dir, cur_var, year, month))))
            dump_file(cur_var, files, out_path, "Diaria|Mensual",
                      len(my_config.vars),
                      my_config)
            last_file = files[0]

        if my_config.template and mk_tmpl:
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)*12
            dump_template(last_file, out_path, "Diaria|Mensual", my_config)

@multiprocesor
def yearly(in_dir, out_dir, year_ini=1961, year_end=2005, **kwargs):
    kwargs = kwargs or {}
    mk_tmpl = kwargs.get("MKTMPL", False)

    for cur_var in ("Prec", "Temp"):
        my_config = copy.copy(config_20km)
        my_config.date_steps = "1yr"
        if cur_var == "Prec":
            my_config.vars = [prec_var]
            my_config.title = "Precipitacion"
        else:
            my_config.vars = [temp_var, tmax_var, tmin_var]
            my_config.title = "Temperatura"

        years = range(year_ini, year_end+1)
        last_file = None
        out_path = os.path.join(out_dir, "Anual", cur_var)
        for year in years:
            files = sorted(glob.glob(os.path.join(in_dir,
                                                  "Mensual/%s/*_%d*01.bin" % (
                                                      cur_var, year))))
            dump_file(cur_var, files, out_path, "Mensual|Anual",
                      len(my_config.vars),
                      my_config)
            last_file = files[0]

        if my_config.template and mk_tmpl:
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)
            dump_template(last_file, out_path, "Mensual|Anual", my_config)

"""Run configurations

A. Generar Mensual/*
====================
1) sumarizar_eta.py mensual 1961,2005
2) sumarizar_eta.py mensual /mnt/oo 2006,2040
3) sumarizar_eta.py mensual 2041,2070

B. Generar Anual/*
1) sumarizar_eta.py anual 1961,2070
"""
if __name__ == '__main__':
    if len(argv) > 1:
        my_module = locals()
        func_obj = None
        args = []
        kwargs = {}
        in_dir = ETA_20K
        out_dir = ETA_20K
        for idx, arg in enumerate(argv[1:]):
            if my_module.get(arg, False):
                func_obj = my_module[arg]
            elif isinstance(arg, basestring):
                in_dir = arg
                out_dir = arg
                args.extend([in_dir, out_dir])
            else:
                try:
                    yi, yf = argv[(idx+1)+1].split(",")
                    args.extend([int(yi), int(yf)])
                except Exception as e:
                    pass
        if func_obj is not None:
            func_obj(*args, **kwargs)
    else:
        print "Usage: ..."
        exit(1)
