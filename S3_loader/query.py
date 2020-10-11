import logging
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from requests import Request

from .get_request import get_request

# if you want to control logs uncomment these lines
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # default logging.WARNING
logger = logging.getLogger()


URL = 'https://scihub.copernicus.eu/dhus/'


MAX_N_IMAGES_IN_REQUEST = 100


def find_images(product_type, period, point, web) -> dict:
    results = {'uuids': [],
               'names': [],
               'dates': [],
               'sizes': [],
               'n_images': 0,
               'point': point,
               'product_type': product_type
               }

    date_start, date_end = period
    lat, lon = point

    q = [
        f'producttype:{product_type}',
        f'beginposition:[{date_start} TO {date_end}]',
        f'footprint:"Intersects({lat}, {lon})"',
        'timeliness:"Non Time Critical"'  # "Near Real Time"
    ]

    payload = {'q': ' AND '.join(q), 'rows': MAX_N_IMAGES_IN_REQUEST}

    start = 0
    url_dhus_search = urljoin(web.url_dhus, 'search')
    url_query = Request('GET', url_dhus_search, params=dict(payload, start=start)).prepare().url
    content, tried = get_request(url_query, web.auth_dhus)

    if content is None:
        logger.error(f'Failed to get query {url_query} after {tried} attempts')
        return results

    results, n_images = parse_request_response(content, results)
    if n_images == 0:
        logger.warning(f'Query returned no results.\n{url_query}')
    logging.info(f'query succeeded: found {n_images} images')

    while n_images - start > 0:
        start += MAX_N_IMAGES_IN_REQUEST
        url_query = Request('GET', url_dhus_search, params=dict(payload, start=start)).prepare().url
        content, tried = get_request(url_query, web.auth_dhus)
        if content is None:
            logger.error(f'Failed to get query {url_query} after {tried} attempts')
            continue
        results, _ = parse_request_response(content, results)
    results['n_images'] = n_images
    return results


def parse_request_response(content, results):
    root = ET.fromstring(content)
    n_images = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text
    assert n_images is not None, 'Error in query url, was date parsed correctly?'
    for e in root.findall('{http://www.w3.org/2005/Atom}entry'):
        results['names'].append(e.find('{http://www.w3.org/2005/Atom}title').text)
        results['uuids'].append(e.find('{http://www.w3.org/2005/Atom}id').text)
        results['dates'].append(e.find('./*[@name="beginposition"]').text)
        results['sizes'].append(e.find('./*[@name="size"]').text)
    return results, int(n_images)
