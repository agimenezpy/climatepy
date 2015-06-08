__author__ = 'agimenez'

import cdms2


class Dataset(object):

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.ds = cdms2.open(self.filename, 'r')
        return self.ds

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ds.close()
