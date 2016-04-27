# -*- coding: utf-8 -*-
from climatepy.grads.files import CtlConfig, CtlVar, CtlFile

__author__ = 'agimenez'

YEARS = (1961, 2070)

config_10km = CtlConfig()
config_20km = CtlConfig()
prec_var = CtlVar()
temp_var = CtlVar()
tmin_var = CtlVar()
tmax_var = CtlVar()

config_10km.grid_x = 330
config_10km.grid_y = 270
config_10km.grid_z = 1
config_10km.times = 1
config_10km.lon = -73
config_10km.lat = -39
config_10km.template = True
config_10km.x_int = 0.1
config_10km.y_int = 0.1

config_20km.grid_x = 166
config_20km.grid_y = 135
config_20km.grid_z = 1
config_20km.times = 1
config_20km.lon = -72.80
config_20km.lat = -38.80
config_20km.template = True
config_20km.x_int = 0.2
config_20km.y_int = 0.2

prec_var.name = "PREC"
prec_var.low = 0
prec_var.high = 99
prec_var.desc = "Total   3h Precip."
prec_var.unit = "(m)"

temp_var.name = "TP2M"
tmin_var.name = "MNTP"
tmax_var.name = "MXTP"
temp_var.low = tmin_var.low = tmax_var.low = 0
temp_var.high = tmin_var.high = tmax_var.high = 99
temp_var.unit = tmin_var.unit = tmax_var.unit = "(K)"
temp_var.desc = "Shelter Temperature"
tmin_var.desc = "Min Temperature"
tmax_var.desc = "Max Temperature"

