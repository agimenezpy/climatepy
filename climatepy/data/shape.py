__author__ = 'agimenez'

import fiona
import numpy as np
import os.path as pth
import shapely.geometry as slygeo
import logging as log
import cPickle as pkl
import math
from collections import OrderedDict


class ShapeMask(object):

    def __init__(self, source, key, lons, lats, cell_size=0.5, cached=True,
                 save=True):

        directory = pth.dirname(source)
        name, ext = pth.splitext(source)
        self.cache = []
        self.index = OrderedDict()
        self.key_field = key

        cache_file = pth.join(directory, name + ".npy")
        index_file = pth.splitext(cache_file)[0] + ".idx"
        if cached:
            if pth.exists(cache_file) and pth.exists(index_file):
                log.info("Load data from cache file %s" % cache_file)
                self.cache = np.load(cache_file)
                self.index = pkl.load(open(index_file, "r"))
            else:
                raise Exception("Cache file must be created")

        self.c = None
        if len(self.cache) == 0:
            self.c = fiona.open(source)

        self.dims = lats, lons
        self.cell_size = cell_size

        if self.c is not None:
            for idx, shape in enumerate(self.c):
                self.cache.append(self.__get_mask(shape))
                key_hole = shape['id']
                if self.key_field != "id":
                    key_hole = self.key_field % shape['properties']
                self.index[key_hole] = idx
            self.c.close()

        if save and not pth.exists(cache_file):
            # Cached masks are stored in numpy arrays
            if isinstance(self.cache, list):
                self.cache = np.array(self.cache)
            log.info("Saving data to cache file %s" % cache_file)
            np.save(cache_file, self.cache)
            pkl.dump(self.index, open(index_file, "wb"))

    def __getitem__(self, item):
        if item in self.index:
            return self.cache[self.index[item]]
        else:
            return None

    def keys(self):
        return self.index.keys()

    def __get_mask(self, shape):
        geom = slygeo.asShape(shape['geometry'])
        mask = np.ones((len(self.dims[0]), len(self.dims[1])), dtype=bool)
        if geom.geom_type in ('MultiPolygon', 'Polygon'):
            bounds = (round_down(geom.bounds[0]), round_down(geom.bounds[1]),
                      round_up(geom.bounds[2]), round_up(geom.bounds[3]))
            is_mask = False
            px, py = -1, -1
            center = geom.centroid
            val = 999
            log.info("Generating mask for %s-%s %r" % (geom.geom_type,
                                                       shape['id'], bounds))
            for y, lat in enumerate(self.dims[0]):
                for x, lon in enumerate(self.dims[1]):
                    if lat < bounds[1] or lat > bounds[3]:
                        continue
                    if lon < bounds[0] or lon > bounds[2]:
                        continue
                    point = slygeo.Point(lon, lat)
                    poly = point.buffer(self.cell_size,
                                        cap_style=slygeo.CAP_STYLE.square)
                    if geom.contains(poly) or geom.intersects(poly):
                        mask[y, x] = False
                        is_mask = True
                    dist = center.distance(point)
                    if dist < val:
                        val = dist
                        px, py = x, y
            all_true = mask.all()
            if not is_mask and all_true:
                mask[py, px] = False
            if all_true:
                log.warn("Mascara no generada para %s" % shape["id"])
            log.info("%d values" % len(mask[mask == False]))
        else:
            raise Exception("Geometry %s not valid for computing mask" %
                            geom.geom_type)
        return mask

    def __len__(self):
        return len(self.cache)


def round_up(number):
    if number < 0:
        return math.trunc(number*10)/10.0
    else:
        return math.floor(number*10)/10.0


def round_down(number):
    if number < 0:
        return math.floor(number*10)/10.0
    else:
        return math.ceil(number*10)/10.0
