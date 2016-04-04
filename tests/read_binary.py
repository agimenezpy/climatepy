# -*- coding: utf-8 -*-
import unittest
import struct
import logging
import cdms2
import os
import numpy as np

__author__ = 'agimenez'

logging.basicConfig(level=logging.INFO)

class TestReadBinary(unittest.TestCase):

    def setUp(self):
        filename = "/Users/agimenez/Desktop/ProyectoCC/escenarios/ETA/Eta_10km/1961_2005/" \
                   "Diario/Temp/Eta_HG2ES_RCP45_10km_Temp_Diaria_19610101"
        self.bindata = open(filename + ".bin", "r")
        self.FILESIZE = os.path.getsize(filename + ".bin")
        self.dset = cdms2.open(filename+".ctl")
        self.ROWS = 270
        self.COLS = 330
        variable = self.dset.listvariables()[0]
        self.vals = self.dset(variable, squeeze=1, time='1961-1-1')

    def test_compare(self):
        size = self.COLS*struct.calcsize("f")
        data = []
        self.bindata.seek(0)
        for idx in range(0, self.ROWS):
            data.append(struct.unpack("=%df" % self.COLS, self.bindata.read(size)))
            self.assertEqual(len(data[-1]), self.COLS)
        logging.info(self.FILESIZE)
        self.assertEqual(len(data), self.ROWS)
        self.assertFalse(self.bindata.read(1))
        self.assertEqual(size*self.ROWS, self.FILESIZE)

        logging.info(self.vals.shape)
        self.assertEqual(self.vals.shape[0], self.ROWS)
        self.assertEqual(self.vals.shape[1], self.COLS)

        #for idx in range(0, self.ROWS):
        #    for jdx in range(0, self.COLS):
        #        self.assertTrue(data[idx][jdx] == self.vals[idx, jdx])
                #logging.debug("%.10f %.10f" % (data[idx][jdx], self.vals[idx,jdx]))

    def test_numpy(self):
        data = []
        #for idx in range(0, self.ROWS):
        data = np.fromfile(self.bindata, dtype=np.float32, count=self.COLS*self.ROWS)
        data = np.reshape(data, (self.ROWS, self.COLS), 'C')
        #logging.info(data[-1])
        self.assertEqual(data.shape[1], self.COLS)
        size = self.COLS*data.itemsize
        self.assertEqual(data.shape[0], self.ROWS)
        self.assertFalse(self.bindata.read(1))
        self.assertEqual(size*self.ROWS, self.FILESIZE)

        logging.info(self.vals.shape)
        self.assertEqual(self.vals.shape[0], self.ROWS)
        self.assertEqual(self.vals.shape[1], self.COLS)


        #logging.info(data == self.vals)
        self.assertTrue((data == self.vals).all())
        #logging.debug("%.10f %.10f" % (data[idx][jdx], self.vals[idx,jdx]))

    def tearDown(self):
        self.bindata.close()
        self.dset.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)