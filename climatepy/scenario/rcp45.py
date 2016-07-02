# -*- coding: utf-8 -*-
import copy
import glob
import itertools
import os

from climatepy.scenario.config import (YEARS, config_20km_rcp45, prec_var,
                                       temp_var, tmin_var, tmax_var)
from climatepy.scenario.summary import (multiprocesor, dump_file, dump_template, get_normal_date)

__author__ = 'agimenez'


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
        my_config = copy.copy(config_20km_rcp45)
        if cur_var == "Prec":
            my_config.vars = [prec_var]
            my_config.title = "Precipitation"
        else:
            my_config.vars = [temp_var, tmax_var, tmin_var]
            my_config.title = "Temperature"
        my_config.date_steps = "1mo"

        out_path = os.path.join(out_dir, "Mensual", cur_var)
        last_file = None
        for year, month in itertools.product(years, months):
            files = sorted(glob.glob(os.path.join(in_dir,
                                           "%s/Diario/%s/*_%d%02d*.bin" %
                                           (root_dir, cur_var, year, month))))
            dump_file(cur_var, files, out_path, "Diaria|Mensual",
                      len(my_config.vars),
                      my_config, 1000, -273)
            last_file = files[0]

        if my_config.template and mk_tmpl:
            my_config.date_init = get_normal_date("%d0101" % YEARS[0])
            my_config.times = (YEARS[1] - YEARS[0] + 1)*12
            dump_template(last_file, out_path, "Diaria|Mensual", my_config)


def yearly(in_dir, out_dir, year_ini=1961, year_end=2005, **kwargs):
    kwargs = kwargs or {}
    mk_tmpl = kwargs.get("MKTMPL", True)
    prec_var.desc = "Precipitacion"

    for cur_var in ("Prec", "Temp"):
        my_config = copy.copy(config_20km_rcp45)
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
