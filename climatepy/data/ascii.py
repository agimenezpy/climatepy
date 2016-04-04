__author__ = 'agimenez'


def export_ascii(filename, data, lats, lons):
    """
    Exports an array of data to ASCII

    :param filename: output filename
    :param data: array of data
    :param lats: latitude coordinates
    :param lons: longitude coordinates
    :return:
    """
    ascw = open(filename+".asc", "w")
    ascw.write("""ncols %d
nrows %d
xllcenter %.2f
yllcenter %.2f
cellsize %.2f
NODATA_value -9999""" % (
        len(lons), len(lats),
        lons[0], lats[0],
        lons[1] - lons[0]))
    for i in reversed(range(0, data.shape[0])):
        ascw.write("\n")
        for j in range(0, data.shape[1]):
            x, y = "%.2f" % lons[j], "%.2f" % lats[i]
            if j > 0:
                ascw.write(" ")
            ascw.write("%.6f" % data[i, j])
    ascw.close()
