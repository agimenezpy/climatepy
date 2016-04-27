# -*- coding: utf-8 -*-
import os
import os.path as pth
import glob
import logging as log
import subprocess as sp

__author__ = 'agimenez'

log.basicConfig(level=log.INFO)


def cmd(*args):
    log.info(" ".join(args))
    ret = sp.call(args)
    if ret > 0:
        raise Exception("Error al ejecutar el comando %s" % args[0])


def check_dir(dir_name):
    if not pth.exists(dir_name):
        os.mkdir(dir_name)


def clean_dir(dir_name, criteria):
    for file_name in iter_dir(dir_name, criteria):
        os.unlink(file_name)


def iter_dir(dir_name, criteria):
    for file_name in sorted(glob.glob(pth.join(dir_name, criteria)),
                            key=pth.basename):
        yield file_name

def empty(dir_name):
    return len(os.listdir(dir_name)) == 0
