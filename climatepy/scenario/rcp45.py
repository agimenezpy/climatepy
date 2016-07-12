# -*- coding: utf-8 -*-
from climatepy.scenario.config import (config_20km_rcp45)
from climatepy.scenario.summary import (multiprocesor, calc_month, calc_year)

__author__ = 'agimenez'


@multiprocesor
def montly(in_dir, out_dir, year_ini=1961, year_end=2005):
    root_dir = ""
    if 1961 <= year_ini <= 2005:
        root_dir = "1961_2005"
    elif 2006 <= year_ini <= 2040:
        root_dir = "2006_2040"
    elif 2040 <= year_ini <= 2070:
        root_dir = "2041_2070"
    # PREC: m -> mm / mes
    # TEMP: K -> C
    params = {"Prec": [0, 1000], "Temp": [-273, 1]}
    calc_month(["Prec", "Temp"], config_20km_rcp45, out_dir, "RCP4.5", in_dir, root_dir, year_ini, year_end,
               params)


def yearly(in_dir, out_dir, year_ini=1961, year_end=2005):
    # PREC: mm/mes
    # TEMP: C
    calc_year(["Prec", "Temp"], config_20km_rcp45, out_dir, "RCP4.5", in_dir, year_ini, year_end)
