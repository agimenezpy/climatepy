# -*- coding: utf-8 -*-
import copy
import glob
import itertools
import os

from climatepy.scenario.config import (YEARS, config_20km_rcp85, prec_var,
                                       temp_var, tmin_var, tmax_var)
from climatepy.scenario.summary import (multiprocesor, dump_file, dump_template, get_normal_date)

__author__ = 'agimenez'


@multiprocesor
def montly(in_dir, out_dir, year_ini=1961, year_end=2005, **kwargs):
    kwargs = kwargs or {}
    mk_tmpl = kwargs.get("MKTMPL", False)
    prec_var.desc = "Precipitacion Total"
    prec_var.unit = "(mm/dia)"
    temp_var.unit = tmin_var.unit = tmax_var.unit = "(C)"

    years = range(year_ini, year_end+1)
    months = range(1, 13)
    root_dir = ""
    if 1961 <= year_ini <= 2005:
        root_dir = "1961-2005"
    elif 2006 <= year_ini <= 2040:
        root_dir = "2006-2040"
    elif 2040 <= year_ini <= 2070:
        root_dir = "2040-2070"
    for cur_var in ("PREC", "TP2M"):
        my_config = copy.copy(config_20km_rcp85)
        if cur_var == "PREC":
            my_config.vars = [prec_var]
            my_config.title = "Precipitacion"
        elif cur_var == "TP2M":
            my_config.vars = [temp_var]
            my_config.title = "Temperatura Media"
        elif cur_var == "MNTP":
            my_config.vars = [tmin_var]
            my_config.title = "Temperatura Minima"
        else:
            assert cur_var == "MXTP"
            my_config.vars = [tmax_var]
            my_config.title = "Temperatura Maxima"
        my_config.date_steps = "1mo"

        out_path = os.path.join(out_dir, "Mensual", cur_var)
        last_file = None
        for year, month in itertools.product(years, months):
            files = sorted(glob.glob(os.path.join(in_dir,
                                           "%s/Diario/%s/*_%d%02d*.bin" %
                                           (root_dir, cur_var, year, month))))
            dump_file(cur_var, files, out_path, "Diario|Mensual",
                      len(my_config.vars),
                      my_config)
            last_file = files[0]

        if my_config.template and mk_tmpl:
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)*12
            dump_template(last_file, out_path, "Diario|Mensual", my_config)


def yearly(in_dir, out_dir, year_ini=1961, year_end=2005, **kwargs):
    kwargs = kwargs or {}
    mk_tmpl = kwargs.get("MKTMPL", True)
    prec_var.desc = "Precipitacion Total"
    prec_var.unit = "(mm/dia)"
    temp_var.unit = tmin_var.unit = tmax_var.unit = "(C)"

    for cur_var in ("PREC", "TP2M"):
        my_config = copy.copy(config_20km_rcp85)
        if cur_var == "PREC":
            my_config.vars = [prec_var]
            my_config.title = "Precipitacion"
        elif cur_var == "TP2M":
            my_config.vars = [temp_var]
            my_config.title = "Temperatura Media"
        elif cur_var == "MNTP":
            my_config.vars = [tmin_var]
            my_config.title = "Temperatura Minima"
        else:
            assert cur_var == "MXTP"
            my_config.vars = [tmax_var]
            my_config.title = "Temperatura Maxima"
        my_config.date_steps = "1yr"

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
