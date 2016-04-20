__author__ = 'agimenez'

import fiona
from collections import OrderedDict
from proceso import ROOT_DIR, SHP_DIR, LOG_FORMAT, OUTPUT_DIR
import logging as log
import os.path as pth
import pandas as pd
import numpy as np
from climatepy.analysis.regression import aproximate
from scipy.stats import scoreatpercentile


def normalize(file_path):
    return pth.splitext(pth.basename(file_path))[0]


def create_output_shp(source_shp, source_data, dest_dir):
    dest_shp = pth.join(dest_dir, normalize(source_shp).split("_")[0]
                        + "_" + normalize(source_data) + ".shp")
    if pth.exists(dest_shp):
        return
    with fiona.open(source_shp) as shape:
        new_schema = dict()
        new_schema['geometry'] = shape.schema['geometry']
        new_schema['properties'] = OrderedDict([(k, v) for k, v in shape.schema['properties'].iteritems()
                                                if k != "SUP_M2" and k != "SUP_Ha"])
        log.info("Loading data from %s" % source_data)
        data = pd.read_csv(source_data, index_col=0, header=0)

        for column in data.index:
            new_schema['properties'][str(column)] = "float:7.4"
        log.info("Writing shapefile %s" % dest_shp)

        with fiona.open(dest_shp, "w",
                        driver=shape.driver,
                        crs=shape.crs,
                        schema=new_schema) as dest:
            for rec in shape:
                del rec['properties']["SUP_M2"]
                del rec['properties']["SUP_Ha"]
                for column in data.index:
                    rec['properties'][str(column)] = data.at[column, rec['properties']['PART']]
                log.info("Writing record %s" % rec['id'])
                dest.write(rec)


def create_output_xls(source_data, dest_dir, stats=False):
    dest_xls = pth.join(dest_dir, normalize(source_data) + ".xlsx")
    if pth.exists(dest_xls):
        return
    log.info("Loading data from %s" % source_data)
    data = pd.read_csv(source_data, index_col=0, header=0)
    data.columns = [col.decode('utf-8', 'ignore') for col in data.columns]
    if stats:
        tendencia = pd.DataFrame(index=data.index, columns=data.columns)
        extremos = pd.DataFrame("", index=data.index, columns=data.columns, dtype=basestring)
        for idx, key in enumerate(data.columns):
            tendencia.values[:, idx] = aproximate(data.index, data.values[:, idx])
            p10 = scoreatpercentile(data.values[:30, idx], 10)
            p90 = scoreatpercentile(data.values[:30, idx], 90)
            extremos.loc[data[key] < p10, key] = "< p10=%.4f" % p10
            extremos.loc[data[key] > p90, key] = "> p90=%.4f" % p90
    log.info("Writing excel %s" % dest_xls)
    #data.T.to_excel(dest_xls)
    with pd.ExcelWriter(dest_xls) as writer:
        data.to_excel(writer, sheet_name="Datos")
        if stats:
            tendencia.to_excel(writer, sheet_name="Tendencia")
            extremos.to_excel(writer, sheet_name="Extremos")

if __name__ == '__main__':
    log.basicConfig(level=log.INFO, format=LOG_FORMAT)
    source_sp = pth.join(ROOT_DIR, SHP_DIR, "Cuencas_Municipios_ZDV/CUENxMUNIxZDV_WGS84_sp.shp")
    #create_output_shp(source_sp, pth.join(OUTPUT_DIR, "mensual_prec.csv"),  OUTPUT_DIR)
    #create_output_shp(source_sp, pth.join(OUTPUT_DIR, "anual_prec.csv"),  OUTPUT_DIR)
    #create_output_shp(source_sp, pth.join(OUTPUT_DIR, "anual_tmed.csv"),  OUTPUT_DIR)
    #create_output_xls(pth.join(OUTPUT_DIR, "mensual_prec.csv"), OUTPUT_DIR)
    #create_output_xls(pth.join(OUTPUT_DIR, "mensual_tmed.csv"), OUTPUT_DIR)
    #create_output_xls(pth.join(OUTPUT_DIR, "anual_sdv_prec.csv"), OUTPUT_DIR, True)
    #create_output_xls(pth.join(OUTPUT_DIR, "anual_sdv_temp.csv"), OUTPUT_DIR, True)
    #create_output_xls(pth.join(OUTPUT_DIR, "anual_tarija_prec.csv"), OUTPUT_DIR)
    #create_output_xls(pth.join(OUTPUT_DIR, "anual_tarija_tmed.csv"), OUTPUT_DIR)
    create_output_xls(pth.join(OUTPUT_DIR, "anual_muni_prec.csv"), OUTPUT_DIR)
    create_output_xls(pth.join(OUTPUT_DIR, "anual_muni_temp.csv"), OUTPUT_DIR)