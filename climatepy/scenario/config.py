# -*- coding: utf-8 -*-
from climatepy.grads.files import CtlConfig, CtlVar, CtlFile

__author__ = 'agimenez'

YEARS = (1961, 2070)

config_20km_rcp45,  config_20km_rcp85 = CtlConfig(), CtlConfig()
prec_var = CtlVar()
temp_var, tmin_var, tmax_var = CtlVar(), CtlVar(), CtlVar()

config_20km_rcp45.grid_x = 166
config_20km_rcp45.grid_y = 135
config_20km_rcp45.grid_z = 1
config_20km_rcp45.times = 1
config_20km_rcp45.lon = -72.80
config_20km_rcp45.lat = -38.80
config_20km_rcp45.template = True
config_20km_rcp45.x_int = 0.2
config_20km_rcp45.y_int = 0.2

config_20km_rcp85.grid_x = 355
config_20km_rcp85.grid_y = 390
config_20km_rcp85.grid_z = 1
config_20km_rcp85.times = 1
config_20km_rcp85.lon = -100.00
config_20km_rcp85.lat = -50.00
config_20km_rcp85.template = True
config_20km_rcp85.x_int = 0.2
config_20km_rcp85.y_int = 0.2

prec_var.name = "PREC"
prec_var.low = 0
prec_var.high = 99
prec_var.desc = "Total Precipitation"
prec_var.unit = "(mm/mes)"

temp_var.name = "TP2M"
tmin_var.name = "MNTP"
tmax_var.name = "MXTP"
temp_var.low = tmin_var.low = tmax_var.low = 0
temp_var.high = tmin_var.high = tmax_var.high = 99
temp_var.unit = tmin_var.unit = tmax_var.unit = "(C)"
temp_var.desc = "Shelter Temperature"
tmin_var.desc = "Min Temperature"
tmax_var.desc = "Max Temperature"
