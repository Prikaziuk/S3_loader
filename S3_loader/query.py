import logging
import xml.etree.ElementTree as ET

from requests import Request

from S3_loader.get_request import get_request
from S3_loader.checker import *

# if you want to control logs uncomment these lines
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # default logging.WARNING
logger = logging.getLogger()


URL = 'https://scihub.copernicus.eu/dhus/search'


MAX_N_IMAGES_IN_REQUEST = 100


def query_copernicus(product_type, period, point, auth):
    results = {'uuids': [],
               'names': [],
               'dates': [],
               'sizes': [],
               'n_images': 0}

    check_product_type(product_type)
    date_start, date_end = parse_period(period)
    lat, lon = parse_point(point)
    results['point'] = (lat, lon)

    q = [
        f'producttype:{product_type}',
        f'beginposition:[{date_start} TO {date_end}]',
        f'footprint:"Intersects({lat}, {lon})"'
    ]

    payload = {'q': ' AND '.join(q), 'rows': MAX_N_IMAGES_IN_REQUEST}

    start = 0
    url_query = Request('GET', URL, params=dict(payload, **{'start': start})).prepare().url
    content, tried = get_request(url_query, auth)

    if content is None:
        logger.error(f'Failed to get query {url_query} after {tried} attempts')
        return results

    results, n_images = parse_request_response(content, results)
    results['n_images'] = n_images
    if n_images == 0:
        logger.warning(f'Query returned no results.\n{url_query}')

    while n_images - start > 0:
        start += MAX_N_IMAGES_IN_REQUEST
        url_query = Request('GET', URL, params=dict(payload, **{'start': start})).prepare().url
        content, tried = get_request(url_query, auth)
        if content is None:
            logger.error(f'Failed to get query {url_query} after {tried} attempts')
            continue
        results, _ = parse_request_response(content, results)
    logging.info(f'query succeeded: found {n_images} images')
    results['n_images'] = n_images
    return results


def parse_request_response(content, results):
    root = ET.fromstring(content)
    n_images = int(root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text)
    for e in root.findall('{http://www.w3.org/2005/Atom}entry'):
        results['names'].append(e.find('{http://www.w3.org/2005/Atom}title').text)
        results['uuids'].append(e.find('{http://www.w3.org/2005/Atom}id').text)
        results['dates'].append(e.find('./*[@name="beginposition"]').text)
        results['sizes'].append(e.find('./*[@name="size"]').text)
    return results, n_images
