import ConfigParser
import glob
from os import path as pth
from sys import platform
import logging as log


def load_all(directory):
    out_values = {}
    for fname in glob.glob(directory + "/*.ini"):
        config = ConfigParser.ConfigParser()
        config.read(fname)
        file_name = pth.splitext(pth.basename(fname))[0]
        out_values[file_name] = config.get("links", platform, "")
    log.debug(out_values)
    return out_values
