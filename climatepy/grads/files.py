# -*- coding: utf-8 -*-
import os
import logging as log
import numpy as np

__author__ = 'agimenez'


class File(object):
    def __init__(self, fullpath):
        self.name = os.path.basename(fullpath)
        self.dir = os.path.dirname(fullpath)

    @property
    def path(self):
        return os.path.join(self.dir, self.name)

    def exists(self):
        return os.path.exists(self.path)

    def read(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        pass


class BinFile(File):
    def __init__(self, fullpath, float_type=np.float32):
        super(BinFile, self).__init__(fullpath)
        self.float_type = float_type

    def read(self, values=1, shape=None):
        num_array = None
        if self.exists():
            num_array = np.fromfile(self.path, dtype=self.float_type, count=values)
        if num_array is not None:
            if shape is not None and len(shape) > 1:
                return np.reshape(num_array, shape, 'C')
            else:
                return num_array
        else:
            return False

    def save(self, num_array=None):
        if num_array is not None and os.path.exists(self.dir):
            try:
                num_array.tofile(self.path)
                log.info("Saving file %s with size %d" % (self.name, os.path.getsize(self.path)))
            except Exception, e:
                log.error(e.message, e)
        else:
            return False

    def check_content(self, size):
        return os.path.getsize(self.path) == size


class CtlConfig(object):
    grid_x = 1
    grid_y = 1
    grid_z = 1
    lon = 0
    lat = 90
    x_int = 0.1
    y_int = 0.1
    levels = []
    times = 1
    date_init = None
    date_steps = "1dy"
    vars = []
    options = []
    template = False

    def to_dict(self):
        return {
            "xn": self.grid_x, "lln": self.lon, "xint": self.x_int,
            "yn": self.grid_y, "llt": self.lat, "yint": self.y_int,
            "zn": self.grid_z, "zlvls": " ".join(self.levels) or "1000",
            "tn": self.times, "dini": self.date_init or "01Jan1961", "dstep": self.date_steps,
            "vars": len(self.vars),
            "varr": [v.to_dict() for v in self.vars] or None,
            "options": self.options or None
        }


class CtlVar(object):
    name = ""
    low = 0
    high = 0
    desc = ""
    unit = ""

    def to_dict(self):
        return {
            "var": self.name,
            "low": self.low,
            "high": self.high,
            "vdesc": self.desc,
            "vunit": self.unit
        }


class CtlFile(File):
    template = """DSET ^{filename}
{options}
UNDEF {undef}

TITLE {title}

XDEF  {xn} LINEAR  {lln}   {xint}
YDEF  {yn} LINEAR  {llt}   {yint}
ZDEF  {zn} LEVELS {zlvls}
TDEF {tn} LINEAR {dini} {dstep}
VARS  {vars}
{extra}

ENDVARS
"""
    var_tmpl = "{var}    {low}  {high}     {vdesc}        {vunit}"

    def __init__(self, fullpath):
        super(CtlFile, self).__init__(fullpath)
        basename = self.name
        self.name = os.path.splitext(basename)[0] + ".ctl"
        self.values = {
            "filename": basename,
            "undef": "-9999.",
            "title": "NN",
            "xn": "1", "lln": "0", "xint": "0.1",
            "yn": "1", "llt": "0", "yint": "0.1",
            "zn": "1", "zlvls": "1000",
            "tn": "1", "dini": "01Jan1961", "dstep": "1dy",
            "vars": "1",
            "extra": "",
            "options": ""
        }
        self.var_values = {
            "var": "NN",
            "low": "0",
            "high": "99",
            "vdesc": "NN",
            "vunit": "NN"
        }

    def read(self):
        return {}

    def save(self, **kwargs):
        tmpl_values = self.values.copy()
        tmpl_values.update(kwargs or {})

        if tmpl_values.get("varr", False):
            vars = tmpl_values.pop("varr")
            extras = []
            for var in vars:
                kvar = self.var_values.copy()
                kvar.update(var or {})
                extras.append(self.var_tmpl.format(**var))

            tmpl_values["extra"] = "\n".join(extras)
        if tmpl_values.get("options", False):
            opts = tmpl_values.pop("options")
            tmpl_values["options"] = "OPTIONS " + (" ".join(opts)) if opts and len(opts) > 0 else ""

        with open(self.path, "w") as fdesc:
            fdesc.write(self.template.format(**tmpl_values))
            log.info("Saving file %s with size %d" % (self.name, os.path.getsize(self.path)))