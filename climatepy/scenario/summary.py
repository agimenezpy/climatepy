# -*- coding: utf-8 -*-
import datetime
import logging as log
import os
import re

from climatepy.grads.ops import avg_data, sum_data
from climatepy.grads.files import BinFile, CtlFile
from climatepy.scenario import DATE_FORMAT, NUM_THREADS
from climatepy.scenario.config import YEARS

__author__ = 'agimenez'


def get_normal_date(basename):
    tuple_date = re.search(DATE_FORMAT, basename).groups()
    year, month, day = map(int, tuple_date)
    return datetime.datetime(year, month, day).strftime("%d%b%Y")


def dump_file(var_name, files, out_dir, alt_name, var_n, config, delta=0, mult=1):
    file_name = os.path.basename(files[0])
    out_name = os.path.splitext(file_name)[0]
    if alt_name:
        out_name = out_name.replace(*alt_name.split("|"))
    config.date_init = get_normal_date(out_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out = os.path.join(out_dir, out_name + ".bin")
    if var_name.upper() == "PREC":
        data = sum_data(files, out, config.grid_y, config.grid_x, var_n, 1, config)
    else:
        data = avg_data(files, out, config.grid_y, config.grid_x, var_n, 1, config)

    count = len(files)
    if count > 1:
        out_obj = BinFile(out)
        out_obj.save(data*mult + delta)

        if config and not config.template:
            out_ctl = CtlFile(out)
            out_ctl.save(**config.to_dict())


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
                log.info("Waiting Thread %s ", cur_thread.name)
                cur_thread.join()

            name = "Thread #%d:%d,%d" % (thread_id, yi, ye)
            log.info("Launch new Thread %s", name)
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
