from os import path as pth

__author__ = 'agimenez'

ETA_10K = pth.join("escenarios", "ETA", "Eta_10km")
ETA_20K = pth.join("escenarios", "ETA", "Eta_20km")
REMOTE_URL = "http://dap.pykoder.com/"
LOG_FORMAT = "%(levelname)s:%(thread)d-%(threadName)s:%(asctime)-15s %(message)s"
DATE_FORMAT = "([0-9]{4})([0-9]{2})([0-9]{2})"
NUM_THREADS = 4

