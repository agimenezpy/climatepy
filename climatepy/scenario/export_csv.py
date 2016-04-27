import os
import csv
import os.path as pth
from climatepy.data import *
from climatepy.scenario.geo import PARAGUAY
import logging as log
import numpy as np

__author__ = 'agimenez'
__licence__ = 'GPL'


class ApplicationException(Exception):
    pass

def export_to(source_ds, source_shp, out_file, var_name, year_end=None,
              extent=PARAGUAY,  mask_key="%(PART)s", cell_size=0.1):
    mascara = None
    if pth.exists(out_file):
        os.unlink(out_file)
    with Dataset(source_ds) as dataset:
        cur_var = dataset.variables.get(var_name, False)
        log.info("Procesando %s", var_name)
        if not cur_var:
            raise ApplicationException("Variable name should be provided")
        with open(out_file, "w") as cvs_output:
            csv_writer = csv.writer(cvs_output)
            time_array = cur_var.getTime().asComponentTime()
            for time_idx, cur_time in enumerate(time_array):
                log.debug("Procesando %s, %d", cur_time, year_end)
                if year_end and cur_time.year > year_end:
                    break
                bound_lat = (extent[0][1], extent[1][1])
                bound_lon = (extent[0][0], extent[1][0])
                data = dataset(cur_var.id, squeeze=1, time=cur_time, 
                               latitude=bound_lat, longitude=bound_lon)

                if cur_var.id == 'prec':
                    data *= 1000  # To mm/day
                else:
                    data -= 273  # To Celsius

                if not mascara:
                    # Cell size of ETA 0.1
                    mascara = ShapeMask(source_shp, mask_key, data.getLongitude()[:],
                                        data.getLatitude()[:], cell_size,
                                        True)
                    names = [claves.encode("utf-8") for claves in
                             mascara.keys()]
                    csv_writer.writerow([""] + names)
                log.debug("Enmascarando datos")
                push_array = ["%d%02d%02d" % (cur_time.year, cur_time.month,
                                              cur_time.day)]
                for k in mascara.keys():
                    mask = mascara[k]
                    masked_data = np.ma.array(data, mask=mask)
                    push_array.append("%.4f" % masked_data.mean())
                csv_writer.writerow(push_array)
        log.info("%d Bytes escritos", pth.getsize(out_file))

