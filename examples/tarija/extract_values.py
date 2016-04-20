__author__ = 'agimenez'
__licence__ = 'GPL'

import getopt
import sys
import os.path as pth
from climatepy.data import *
from proceso import ETA_10K, ROOT_DIR, SHP_DIR, LOG_FORMAT, BOUND_LAT, BOUND_LON, get_remote_file
import logging as log
import numpy as np
import csv


class ApplicationException(Exception):
    pass


def usage_and_exit(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApplicationException as err:
            print str(err)
            usage()
            sys.exit(1)
        except:
            raise
    return wrapper


@usage_and_exit
def main(argv):
    opts, args = getopt.getopt(argv, "ho:n:var:v", ["help", "output"])
    output = None
    var_name = None
    log_opts = {"format": LOG_FORMAT}
    oargs = {}
    for o, a in opts:
        if o == "-v":
            log_opts['level'] = log.INFO
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ('-o', '--output'):
            output = a
        elif o == '-n':
            try:
                oargs["year_end"] = int(a)
            except Exception as e:
                raise ApplicationException(e.message)
        elif o == '-r':
            var_name = a

    if len(args) < 2:
        raise ApplicationException("Not enough arguments")
    log.basicConfig(**log_opts)

    file_in1 = pth.join(ETA_10K, args[0])
    file_in2 = pth.join(SHP_DIR, args[1])
    log.info("Input dataset %s " % file_in1)
    log.info("Input shape %s " % file_in2)
    if pth.exists(file_in1) and pth.exists(file_in2):
        if not pth.dirname(output):
            output_dir = pth.dirname(__file__)
            output = pth.join(output_dir, output)
        else:
            output_dir = pth.dirname(output)
        log.info("Output file %s" % output)
        if output and pth.exists(output_dir):
            if sys.platform == "win32":
                file_in1 = get_remote_file(file_in1)
                print file_in1
            export_to(file_in1, file_in2, output, var_name, **oargs)
        else:
            raise ApplicationException("Destination directory doesn't exists")
    else:
        raise ApplicationException("Source dataset/shape file doesn't exists")


def export_to(source_ds, source_shp, out_file, var_name, year_end=None):
    mascara = None
    with Dataset(source_ds) as dataset:
        cur_var = dataset.variables.get(var_name, False)
        if not cur_var:
            raise ApplicationException("Variable name should be provided")
        with open(out_file, "w") as cvs_output:
            csv_writer = csv.writer(cvs_output)
            time_array = cur_var.getTime().asComponentTime()
            for time_idx, cur_time in enumerate(time_array):
                log.info("Procesando %s, %d" % (cur_time, year_end))
                if year_end and cur_time.year > year_end:
                    break
                data = dataset(cur_var.id, squeeze=1, time=cur_time, latitude=BOUND_LAT, longitude=BOUND_LON)

                if cur_var.id == 'prec':
                    data *= 1000  # To mm/day
                else:
                    data -= 273  # To Celsius

                if not mascara:
                    # Cell size of ETA 0.1
                    mascara = ShapeMask(source_shp, "%(PART)s", data.getLongitude()[:],
                                        data.getLatitude()[:], 0.1, True)
                    csv_writer.writerow([""] + [strU.encode("utf-8") for strU in mascara.keys()])
                log.info("Enmascarando datos")
                push_array = ["%d%02d%02d" % (cur_time.year, cur_time.month, cur_time.day)]
                for k in mascara.keys():
                    mask = mascara[k]
                    masked_data = np.ma.array(data, mask=mask)
                    push_array.append("%.4f" % masked_data.mean())
                csv_writer.writerow(push_array)
        log.info("%d Bytes escritos" % pth.getsize(out_file))


def usage():
    print """Usage %s: [-h|--help -v|-n num_years} -r variable_name -o|--output output_file input_dataset input_shapefile

Options
  -h or --help: prints helps
  -v: set verbosity level
  -o or --output: output file name
  -n: year quantity to output
  -r: variable name to output
Arguments
  input_dataset: CDMS file to process
  input_shapefile: Shapefile to process
""" % sys.argv[0]

# Run with (1)
# -v
# -o../salida/mensual_prec.csv
# -r prec
# -n2050
# Mensual/Prec/Eta_HG2ES_RCP45_10km_Prec_Mensual_template.ctl
# Cuencas_Municipios_ZDV/CUENxMUNIxZDV_WGS84_sp.shp

# Run with (2)
# -v
# -o../salida/mensual_tmed.csv
# -r tp2m
# -n2050
# Mensual/Temp/Eta_HG2ES_RCP45_10km_Temp_Mensual_template.ctl
# Cuencas_Municipios_ZDV/CUENxMUNIxZDV_WGS84_sp.shp

# Run with (3)
# python proceso\extract_values.py -v -osalida\anual_sdv_prec.csv -r prec -n2050 Anual\Prec\Eta_HG2ES_RCP45_10km_Prec_Anual_template.ctl Tarija_New_SDV\Tarija_New_SDV.shp
# python proceso\extract_values.py -v -osalida\anual_sdv_temp.csv -r tp2m -n2050 Anual\Temp\Eta_HG2ES_RCP45_10km_Temp_Anual_template.ctl Tarija_New_SDV\Tarija_New_SDV.shp

# Run with (4)
# python proceso\extract_values.py -v -osalida\anual_muni_prec.csv -r prec -n2050 Anual\Prec\Eta_HG2ES_RCP45_10km_Prec_Anual_template.ctl shp\tarija_muni.shp
# python proceso\extract_values.py -v -osalida\anual_muni_temp.csv -r tp2m -n2050 Anual\Temp\Eta_HG2ES_RCP45_10km_Temp_Anual_template.ctl shp\tarija_muni.shp
if __name__ == '__main__':
    main(sys.argv[1:])
