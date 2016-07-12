from os import path as pth

__author__ = 'agimenez'

RCP_45 = pth.join("RCP4.5", "Eta_20km")
RCP_85 = pth.join("RCP8.5", "Eta_20km")
REMOTE_URL = "http://dap.pykoder.com/"
LOG_FORMAT = "%(levelname)s:%(thread)d-%(threadName)s:%(asctime)-15s %(message)s"
DATE_FORMAT = "([0-9]{4})([0-9]{2})([0-9]{2})"
DATE_FORMAT_SHORT = "([0-9]{4})([0-9]{2})"
NUM_THREADS = 4

