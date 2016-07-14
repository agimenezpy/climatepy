import os
import os.path as pth
import glob
from collections import OrderedDict
import logging as log

import fiona

from climatepy.scenario.geo import PARAGUAY
from climatepy.data import *

__author__ = 'agimenez'

def clean_shp(dest_dir):
    files = pth.splitext(dest_dir)[0] + ".*"
    for filep in glob.glob(files):
        os.unlink(filep)

def to_dict(poly):
    return {"type": "Polygon", "coordinates": poly}


def simple(shape):
    props, geom = shape['properties'], shape['geometry']
    if geom['type'] == "Polygon":
        return iter([(shape["id"], props, geom)])
    elif geom['type'] == 'MultiPolygon':
        return iter((
            ("%s-%02d" % (shape["id"], idx), props, to_dict(g))
                     for idx, g in enumerate(geom['coordinates'])
        ))
    else:
        raise Exception("Invalid geometry")


def copy_schema(schema):
    schema_list = [("PART", "str:10")]
    schema_list.extend([(k, v) for k, v in schema["properties"].iteritems()])
    return {"properties": OrderedDict(schema_list),
            "geometry": "Polygon"}


def simplify(source_shp, delete=True):
    dest_shp = pth.join(pth.dirname(source_shp),
                        pth.splitext(pth.basename(source_shp))[0] + "_sp.shp")
    if delete and pth.exists(dest_shp):
        clean_shp(dest_shp)
    else:
        return dest_shp
    with fiona.open(source_shp) as collection:
        schema_new = copy_schema(collection.schema)
        with fiona.open(dest_shp, "w",
                        driver=collection.driver,
                        crs=collection.crs,
                        schema=schema_new) as sink:
            for shp in collection:
                for ident, feat, simgeo in simple(shp):
                    rec = dict()
                    rec["id"] = -1
                    feat["PART"] = ident
                    rec["properties"] = feat
                    rec["geometry"] = {"type": "Polygon", "coordinates": simgeo["coordinates"]}
                    sink.write(rec)
    return dest_shp


def create_masks(source_ds, source_shp, extent=PARAGUAY, key="%(PART)s",
                 cell_size=0.1):
    if pth.exists(source_shp):
        with Dataset(source_ds) as dset:
            bound_lat = (extent[0][1], extent[1][1])
            bound_lon = (extent[0][0], extent[1][0])
            data = dset(dset.listvariables()[0], squeeze=1,
                        time='1961-01-01', latitude=bound_lat,
                        longitude=bound_lon)
            log.info(data.shape)
            mascara = ShapeMask(source_shp, key, data.getLongitude()[:],
                                data.getLatitude()[:], cell_size, False)
            log.info("DONE")
    else:
        raise Exception("Shape file %s doesn't exists" % source_shp)
