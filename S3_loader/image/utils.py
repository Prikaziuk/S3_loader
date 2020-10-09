import math
import os
import xml.etree.ElementTree as ET

from shapely.geometry import Point, Polygon

DEG_TO_RAD = math.pi / 180


def make_polygon_wkt(lat, lon, *, km_shift=None, deg_shift=None):
    if km_shift:
        shift_lat, shift_lon = get_offset_deg_from_km(lat, km_shift)
    elif deg_shift:
        shift_lat = shift_lon = deg_shift
    else:
        raise Exception('Neither deg_shift nor km_shift were provided')
    borders = {'lat_up': lat + shift_lat,
               'lat_down': lat - shift_lat,
               'lon_left': lon - shift_lon,
               'lon_right': lon + shift_lon}
    wkt = "POLYGON ((" \
          "{lon_left} {lat_up}, {lon_right} {lat_up}," \
          "{lon_right} {lat_down}, {lon_left} {lat_down}," \
          "{lon_left} {lat_up}" \
          "))".format(**borders)
    return wkt


def get_offset_deg_from_km(lat_deg, distance_km):
    """
    Calculates offset in degrees based on latitude in degrees and shift in meters

    :param float lat_deg:
    :param float distance_km: shift from the latitude N and E
    :return: (offset_lat, offset_lon)
    :rtype: tuple[(float, float)]
    """
    rlat = lat_deg * DEG_TO_RAD
    met_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * rlat) + 1.175 * math.cos(4 * rlat)

    met_per_deg_lon = 111412.84 * math.cos(rlat) - 93.5 * math.cos(3 * rlat)

    offset_lat = distance_km / met_per_deg_lat * 1000
    offset_lon = distance_km / met_per_deg_lon * 1000

    # print(met_per_deg_lat, met_per_deg_lon)
    return offset_lat, offset_lon


def intersects(product_dir_path, lat, lon):
    # read geometry from xml with ET
    root = ET.parse(os.path.join(product_dir_path, 'xfdumanifest.xml'))
    footprint = root.find(r'metadataSection/metadataObject/metadataWrap/xmlData/'
                          r'{http://www.esa.int/safe/sentinel/1.1}frameSet/'
                          r'{http://www.esa.int/safe/sentinel/1.1}footPrint/'
                          r'{http://www.opengis.net/gml}posList').text.split()
    # check intersection of geometry with polygon (site centre is better)
    # lon, lat
    polygon = [[float(footprint[i + 1]), float(footprint[i])] for i in range(0, len(footprint), 2)]
    return Polygon(polygon).contains(Point(lon, lat))
