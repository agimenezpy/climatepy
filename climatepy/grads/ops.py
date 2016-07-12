# -*- coding: utf-8 -*-
import logging as log
import time

import numpy as np

from climatepy.grads.files import BinFile

__author__ = 'agimenez'


def collect_files(file_names):
    for file_name in file_names:
        yield BinFile(file_name)


def collect_data(file_names, rows, cols, vars_n=1, dim=1):
    files = collect_files(file_names)
    if dim == 1:
        dims = (rows*cols*vars_n,)
    else:
        dims = (vars_n, rows, cols)

    # 4 Bytes for Float32
    accumulator = np.zeros(dims, dtype=np.float32)
    count = 0
    t_s = time.time()
    for file_obj in files:
        same_size = file_obj.check_content(rows*cols*vars_n*4)
        data = file_obj.read(rows*cols*vars_n, dims)
        if data is False or not same_size:
            log.error("Error al procesar %s" % file_obj.name)
            continue
        accumulator = accumulator + data
        count += 1
    log.info("Procesando %d archivo(s) en %.2f segundos" % (count, time.time() - t_s))
    return accumulator, count


def sum_data(file_names, rows, cols, vars_n=1, dim=1):
    acc, count = collect_data(file_names, rows, cols, vars_n, dim)

    return acc


def avg_data(file_names, rows, cols, vars_n=1, dim=1):
    acc, count = collect_data(file_names, rows, cols, vars_n, dim)

    return acc / count


def crop(file_name, out_file, rows, cols, vars_n=1, dim=1, config=None):
    pass

if __name__ == '__main__':
    pass
