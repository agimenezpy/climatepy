# -*- coding: utf-8 -*-
from climatepy.data.dataset import Dataset
from climatepy.data.shape import ShapeMask
import getopt
import numpy as np
import logging as log
import unittest

__author__ = 'agimenez'

TEST_DS = "/Users/agimenez/Desktop/ProyectoCC/escenarios/ETA/Eta_10km/" \
          "Mensual/Prec/Eta_HG2ES_RCP45_10km_Prec_Mensual_template.ctl"
TEST_SHP = "/Users/agimenez/Desktop/ProyectoCC/" \
           "tarija/alcance/Cuencas_Municipios_ZDV/CUENxMUNIxZDV_WGS84_sp.shp"


class TestCase(unittest.TestCase):
    def setUp(self):
        log.basicConfig(level=log.INFO)

    def test_open(self):
        with Dataset(TEST_DS) as dataset:
            self.assertEqual(dataset('prec', time='1961-1-1').shape[0], 1)
            self.assertEqual(dataset['prec'][0].shape[0], 270)

    def test_args(self):
        opts, args = getopt.getopt(["-h", "-v", "-o1", "-var tete", "Root/Toor"], "ho:var:v", ["help", "output"])
        print opts, args
        self.assertEqual(len(args), 1)

    def test_shape_nocached(self):
        lons = np.arange(-67.5, -61.45, 0.1)
        lats = np.arange(-23.5, -18.45, 0.1)
        masks = ShapeMask(TEST_SHP, "%(PART)s", lons, lats, 0.1)
        print len(masks)

    def test_loadshape(self):
        pass