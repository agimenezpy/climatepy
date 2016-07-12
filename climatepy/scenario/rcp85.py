# -*- coding: utf-8 -*-
from climatepy.scenario.config import config_20km_rcp85
from climatepy.scenario.summary import (multiprocesor, calc_month, calc_year, calc_month2month)

__author__ = 'agimenez'


@multiprocesor
def montly(in_dir, out_dir, year_ini=1961, year_end=2005):
    root_dir = ""
    if 1961 <= year_ini <= 2005:
        root_dir = "1961-2005"
    elif 2006 <= year_ini <= 2040:
        root_dir = "2006-2040"
    elif 2040 <= year_ini <= 2070:
        root_dir = "2040-2070"

    # PREC: mm/day -> mm/mes
    # TEMP: C
    calc_month(["PREC", "TP2M"], config_20km_rcp85, out_dir, "RCP8.5", in_dir, root_dir, year_ini, year_end)


def montly2(in_dir, out_dir, year_ini=1961, year_end=2005):
    root_dir = ""
    if 1961 <= year_ini <= 2005:
        root_dir = "1961-2005"
    elif 2006 <= year_ini <= 2040:
        root_dir = "2007-2040"
    elif 2040 <= year_ini <= 2070:
        root_dir = "2041-2070"

    # PREC: mm/day -> mm/mes (multiplicar por 30)
    # TEMP: C
    params = {"PREC": [0, 30]}
    calc_month2month(["PREC", "TP2M"], config_20km_rcp85, out_dir, "RCP8.5", in_dir, root_dir, year_ini, year_end,
                     params)


def yearly(in_dir, out_dir, year_ini=1961, year_end=2005):
    # PREC: mm/mes
    # TEMP: C
    calc_year(["PREC", "TP2M"], config_20km_rcp85, out_dir, "RCP8.5", in_dir, year_ini, year_end)
