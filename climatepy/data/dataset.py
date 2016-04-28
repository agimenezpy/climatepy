# -*- coding: utf-8 -*-

__author__ = 'agimenez'


class Dataset(object):
    """
    CDAT dataset wrapper
    """

    def __init__(self, filename):
        """
        Constructor requires sets a Grads filename

        :param filename: a file with grads format
        """
        self.filename = filename

    def __enter__(self):
        """
        Returns a dataset descriptor
        :return:
        """
        import cdms2
        self.ds = cdms2.open(self.filename, 'r')
        return self.ds

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close dataset
        """
        self.ds.close()
