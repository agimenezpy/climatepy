import fiona
import os
from collections import OrderedDict
import logging as log
import os.path as pth
import pandas as pd
import numpy as np
from climatepy.analysis.regression import aproximate

__author__ = 'agimenez'

def normalize(file_path):
    return pth.splitext(pth.basename(file_path))[0]


def get_names(source_shp, columns, map_key, name_prop):
    with fiona.open(source_shp) as collection:
        names_dict = {}
        for idx, shape in enumerate(collection):
            names_dict[map_key % shape['properties']] = \
                name_prop % shape['properties']

    names = [names_dict[claves].encode("utf-8") for claves in columns]
    return names

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


def create_montly_xls(source_data, source_shp, dest_dir, map_key, name_prop):
    dest_xls = pth.join(dest_dir, normalize(source_data) + ".xlsx")
    if pth.exists(dest_xls):
        os.unlink(dest_xls)
    log.info("Loading data from %s" % source_data)
    data = pd.read_csv(source_data, index_col=0, header=0, parse_dates=True)
    names = get_names(source_shp, data.columns, map_key, name_prop)
    data.columns = [col.decode('utf-8', 'ignore') for col in names]
    log.info("Writing excel %s" % dest_xls)
    with pd.ExcelWriter(dest_xls) as writer:
        for period in [(1961, 1990), (2011, 2020),
                       (2021, 2030), (2031, 2040),
                       (2041, 2050)]:
            time_frame = data.index[(data.index.year >= period[0]) &
                                    (data.index.year <= period[1])]
            subset = data.loc[time_frame.values, :]
            subset.to_excel(writer, sheet_name="%d_%d" % period)

def create_yearly_xls(source_data, source_shp, dest_dir, map_key, name_prop):
    dest_xls = pth.join(dest_dir, normalize(source_data) + ".xlsx")
    if pth.exists(dest_xls):
        os.unlink(dest_xls)
    log.info("Loading data from %s" % source_data)
    data = pd.read_csv(source_data, index_col=0, header=0, parse_dates=True)
    data.index = [idx.year for idx in data.index]
    names = get_names(source_shp, data.columns, map_key, name_prop)
    data.columns = [col.decode('utf-8', 'ignore') for col in names]
    period = data.index[data.index > 2010]
    tendencia = pd.DataFrame(index=period, columns=data.columns)
    extremos = pd.DataFrame("", index=period, columns=data.columns,
                            dtype=basestring)
    for idx, key in enumerate(data.columns):
        tendencia.values[:, idx] = aproximate(period, data.loc[2011:, key].values)
        p10 = np.percentile(data.loc[:1991, key].values, 10)
        p90 = np.percentile(data.loc[:1991, key].values, 90)
        extremos.loc[data[key] < p10, key] = "< p10=%.4f" % p10
        extremos.loc[data[key] > p90, key] = "> p90=%.4f" % p90
    log.info("Writing excel %s" % dest_xls)
    with pd.ExcelWriter(dest_xls) as writer:
        for period in [(1961, 1990), (2011, 2020),
                       (2021, 2030), (2031, 2040),
                       (2041, 2050)]:
            subset = data.loc[period[0]:period[1], :]
            subset.T.to_excel(writer, sheet_name="%d_%d" % period)
        tendencia.T.to_excel(writer, sheet_name="Tendencia")
        extremos.T.to_excel(writer, sheet_name="Extremos")
