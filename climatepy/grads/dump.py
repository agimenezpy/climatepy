# -*- coding: utf-8 -*-
import datetime
import re
from os import path as pth, makedirs
from threading import Lock

from climatepy.grads.files import BinFile, CtlFile
from climatepy.grads.ops import avg_data, sum_data
from climatepy.scenario import DATE_FORMAT, DATE_FORMAT_SHORT

__author__ = 'agimenez'

lock = Lock()


def get_normal_date(basename):
    matches = re.search(DATE_FORMAT, basename)
    if matches is not None:
        tuple_date = matches.groups()
        year, month, day = map(int, tuple_date)
    else:
        matches = re.search(DATE_FORMAT_SHORT, basename)
        tuple_date = matches.groups()
        year, month = map(int, tuple_date)
        day = 1
    return datetime.datetime(year, month, day).strftime("%d%b%Y")


def is_full_date(dateformat):
    matches = re.search(DATE_FORMAT, dateformat)
    return matches is not None


def dump_file(files, out_dir, alt_name, var_n, config, avg=True, delta=0, mult=1):
    file_name = pth.basename(files[0])
    out_name = pth.splitext(file_name)[0]
    if alt_name:
        src_string, repl = alt_name.split("|")
        out_name = re.sub("(:?" + src_string + ")", repl, out_name)
    if not pth.exists(out_dir):
        makedirs(out_dir)
    if is_full_date(out_name):
        out = pth.join(out_dir, out_name + ".bin")
    else:
        out = pth.join(out_dir, out_name + "01.bin")

    if avg:
        data = avg_data(files, config.grid_y, config.grid_x, var_n, 1)
    else:
        data = sum_data(files, config.grid_y, config.grid_x, var_n, 1)

    out_obj = BinFile(out)
    out_obj.save(data*mult + delta)

    if config and not config.template:
        config.date_init = get_normal_date(out_name)
        out_ctl = CtlFile(out)
        out_ctl.save(**config.to_dict())


def dump_template(file_base, out_dir, alt_name, config):
    file_name = pth.basename(file_base)
    out_name = pth.splitext(file_name)[0]
    if alt_name:
        out_name = out_name.replace(*alt_name.split("|"))
    tmpl_name = re.sub(DATE_FORMAT, "template", out_name)
    bin_name = re.sub(DATE_FORMAT, "%y4%m2%d2", out_name) + ".bin"
    out = pth.join(out_dir, tmpl_name + ".bin")
    ctlfile = CtlFile(out)
    config.options = ["TEMPLATE"]
    values = config.to_dict()
    values["filename"] = bin_name
    ctlfile.save(**values)