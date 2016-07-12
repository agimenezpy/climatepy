# -*- coding: utf-8 -*-
import copy
import glob
import itertools
import logging as log
import os
from os import path as pth
from threading import Thread

from climatepy.grads.dump import (dump_file, dump_template, get_normal_date)
from climatepy.scenario import NUM_THREADS, DATE_FORMAT_SHORT
from climatepy.scenario.config import (YEARS, prec_var, temp_var, tmin_var, tmax_var)

__author__ = 'agimenez'


def get_config(initial_config, var_name, steps):
    my_config = copy.copy(initial_config)
    my_config.date_steps = steps
    if var_name == "Prec":
        my_config.vars = [prec_var]
        my_config.title = "Precipitation"
    elif var_name == "Temp":
        my_config.vars = [temp_var, tmax_var, tmin_var]
        my_config.title = "Temperatura"
    elif var_name == "PREC":
        my_config.vars = [prec_var]
        my_config.title = "Precipitacion"
    elif var_name == "TP2M":
        my_config.vars = [temp_var]
        my_config.title = "Temperatura Media"
    elif var_name == "MNTP":
        my_config.vars = [tmin_var]
        my_config.title = "Temperatura Minima"
    else:
        assert var_name == "MXTP"
        my_config.vars = [tmax_var]
        my_config.title = "Temperatura Maxima"
    return my_config


def calc_month(all_vars, initial_config, out_dir, model, in_dir, root_dir, year_ini, year_end, params={}):
    make_config = year_ini == 1961
    years = range(year_ini, year_end+1)
    months = range(1, 13)

    for cur_var in all_vars:
        my_config = get_config(initial_config, cur_var, "1mo")

        out_path = pth.join(out_dir, model, "Mensual", cur_var)
        calc_avg = cur_var.upper() != "PREC"
        values = params.get(cur_var, [])
        for year, month in itertools.product(years, months):
            files = sorted(glob.glob(pth.join(in_dir, "%s/Diario/%s/*_%d%02d*.bin" %
                                              (root_dir, cur_var, year, month))))
            dump_file(files, out_path, "Diari.|Mensual", len(my_config.vars), my_config, calc_avg, *values)

        if make_config:
            first_file = os.listdir(out_path)[0]
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1) * 12
            dump_template(first_file, out_path, False, my_config)


def calc_month2month(all_vars, initial_config, out_dir, model, in_dir, root_dir, year_ini, year_end, params={}):
    make_config = year_ini == 1961
    years = range(year_ini, year_end+1)
    months = range(1, 13)

    for cur_var in all_vars:
        my_config = get_config(initial_config, cur_var, "1mo")

        out_path = pth.join(out_dir, model, "Mensual", cur_var)
        calc_avg = cur_var.upper() != "PREC"
        values = params.get(cur_var, [])
        for year, month in itertools.product(years, months):
            files = sorted(glob.glob(pth.join(in_dir, "%s/Mensual/%s/*_%d%02d.bin" %
                                              (root_dir, cur_var, year, month))))
            dump_file(files, out_path, "Mens.a?l|Mensual", len(my_config.vars), my_config, calc_avg, *values)

        if make_config:
            first_file = os.listdir(out_path)[0]
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1) * 12
            dump_template(first_file, out_path, False, my_config)


def calc_year(all_vars, initial_config, out_dir, model, in_dir, year_ini, year_end, params={}):
    make_config = year_ini == 1961

    for cur_var in all_vars:
        my_config = get_config(initial_config, cur_var, "1yr")

        out_path = pth.join(out_dir, model, "Anual", cur_var)
        values = params.get(cur_var, [])
        for year in xrange(year_ini, year_end+1):
            files = sorted(glob.glob(os.path.join(in_dir, "Mensual/%s/*_%d*01.bin" %
                                                          (cur_var, year))))
            dump_file(files, out_path, "Mensual|Anual", len(my_config.vars), my_config, True, *values)

        if make_config:
            first_file = os.listdir(out_path)[0]
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)
            dump_template(first_file, out_path, False, my_config)


def multiprocesor(func):
    def calc_mp(in_dir, out_dir, year_ini=1961, year_end=2005):
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
                log.info("Waiting Thread %s ", cur_thread.name)
                cur_thread.join()

            name = "Thread #%d:%d,%d" % (thread_id, yi, ye)
            log.info("Launch new Thread %s", name)
            cur_thread = Thread(None, func, name, [in_dir, out_dir, yi, ye])
            cur_thread.start()
            thread_childs.append(cur_thread)
            thread_id += 1

        while len(thread_childs) > 0:
            cur_thread = thread_childs.pop(0)
            if cur_thread.is_alive():
                cur_thread.join()

    return calc_mp
