__author__ = 'agimenez'

import os.path as pth
import fiona
from collections import OrderedDict
from proceso import ROOT_DIR, ETA_10K, SHP_DIR, BOUND_LON, BOUND_LAT, LOG_FORMAT, get_remote_file
from climatepy.data import *
import logging as log
import os


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


def clean_files(dest_shp):
    files = pth.splitext(dest_shp)[0] + ".*"
    import glob
    for filep in glob.glob(files):
        os.unlink(filep)


def simplify(source_shp, delete=True):
    dest_shp = pth.join(pth.dirname(source_shp),
                        pth.splitext(pth.basename(source_shp))[0] + "_sp.shp")
    if delete and pth.exists(dest_shp):
        clean_files(dest_shp)
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


def create_masks(source_ds, source_shp, key="%(PART)s"):
    if pth.exists(source_shp):
        with Dataset(source_ds) as dset:
            data = dset(dset.listvariables()[0], squeeze=1,
                        time='1961-01-01', latitude=BOUND_LAT, longitude=BOUND_LON)
            print data.shape
            mascara = ShapeMask(source_shp, key, data.getLongitude()[:],
                                data.getLatitude()[:], 0.1, True)
    else:
        raise Exception("Shape file %s doesn't exists" % source_shp)

def create_shp1():
    source_sp = pth.join(ROOT_DIR, SHP_DIR, "Cuencas_Municipios_ZDV/CUENxMUNIxZDV_WGS84.shp")
    source_d = pth.join(ROOT_DIR, ETA_10K, "Mensual/Prec/Eta_HG2ES_RCP45_10km_Prec_Mensual_template.ctl")
    dest_sp = simplify(source_sp, False)
    create_masks(source_d, dest_sp)

if __name__ == '__main__':
    log.basicConfig(level=log.INFO, format=LOG_FORMAT)
    #create_shp1()
    source_d = get_remote_file(pth.join(ETA_10K, r"Anual\Prec\Eta_HG2ES_RCP45_10km_Prec_Anual_template.ctl"))
    print source_d
    #create_masks(source_d,
    #             pth.join(ROOT_DIR, SHP_DIR, "Tarija_New_SDV", "Tarija_New_SDV_WGS84.shp"),
    #             "SDV_%(COD_SDV)s:%(UNIDADES)s")
    create_masks(source_d,
                 pth.join(ROOT_DIR, SHP_DIR, "shp", "tarija_muni.shp"),
                 "MUN_%(CODIGO)s:%(NOM_MUN)s")