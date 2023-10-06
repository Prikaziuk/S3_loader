"""
Package to query for ESA Sentinel-3 products and download them.
(c) Prikaziuk 2020, prikaziuk@gmail.com
"""
import logging
from collections import namedtuple
from pathlib import Path
from urllib.parse import urljoin

import requests


from .checker import parse_point, parse_period, check_product_type, check_point_in_db, parse_names
from .database import Database
from .download import download_parallel, make_url_daac, get_orbits
from .query import find_images

try:
    from . import config_my as config
except ImportError:
    from . import config

logging.basicConfig(level=logging.INFO)

Web = namedtuple('Web', ['url_dhus', 'auth_dhus', 'url_daac', 'api_key_daac'])

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/70.0.3538.77 ' +
                      'Safari/537.36 ' +
                      'Edg/79.0.309.43',
        'Authorization': ''
    }


class S3Loader:
    # URL_DHUS = 'https://colhub.met.no/'
    # URL_DHUS = 'https://coda.eumetsat.int/'
    URL_DHUS = 'https://apihub.copernicus.eu/apihub/'
    URL_DAAC = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/'

    def __init__(self, db_path):
        self.db_path = db_path
        if config.AUTH[0] == 'DHUS_username':
            raise Exception(f'Please, replace placeholders with valid Copernicus credentials in S3_Loader/config.py')
        self.web = Web(url_dhus=self.URL_DHUS, auth_dhus=config.AUTH,
                       url_daac=self.URL_DAAC, api_key_daac=config.DAAC_API_KEY)

    def query(self, product_type, period, point):
        check_product_type(product_type)
        period = parse_period(period)
        point = parse_point(point)

        db = Database(self.db_path)
        check_point_in_db(db, point)
        db.close()

        images = find_images(product_type, period, point, self.web)
        self._images2db(images)

    def _images2db(self, images):
        db = Database(self.db_path)
        point = images['point']
        db.create_points_table()
        db.insert_point(point)

        product_type = images['product_type']
        db.create_products_table(product_type)
        images['point_id'] = [db.get_point_id(point)] * images['n_images']
        db.insert_images(images, product_type)
        db.close()
        logging.info(f'Images successfully inserted into {product_type} table of {self.db_path}')

    def download(self, product_type, load_dir=None, names=None, period=None, parallel=False, orbits=False):
        check_product_type(product_type)
        if period is not None:
            period = parse_period(period)
        if names is not None:
            names = parse_names(names)

        db = Database(self.db_path)
        uuids_names = db.select_uuids_names(product_type, period, names)
        db.close()
        if len(uuids_names) == 0:
            err_msg = f'no non-loaded products found in the database table {product_type} (==product type)'
            if period is not None:
                err_msg += f' for the period {period}'
            if names is not None:
                err_msg += f', names did not match any of the {len(names)} product names provided'
            err_msg += '\nquiting...'
            logging.warning(err_msg)
            return

        if orbits:
            if period is not None:
                raise Exception('period should be None to download only the frequent orbits. Is orbits=True a mistake?')
            if names is not None:
                raise Exception('names should be None to download only the frequent orbits. Is orbits=True a mistake?')
            uuids_names = get_orbits(uuids_names)

        logging.info(f'Found {len(uuids_names)} products to download. Expected different number - redo the query')

        if load_dir is None:
            load_dir = product_type
        load_dir = Path(load_dir)
        load_dir.mkdir(exist_ok=True, parents=True)
        logging.info(f'Images will be downloaded to {load_dir}')

        download_parallel(uuids_names, load_dir, self.web, parallel=parallel)

    # TODO with s = requests.Session(), s.auth=auth(), s.get is 30% faster than individual requests.get()

    def set_offline(self, product_type, period=None, names=None):
        logging.info(f'Checking if products are offline in LTA')
        db = Database(self.db_path)
        s = requests.Session()
        s.auth = self.web.auth_dhus
        uuids_names = db.select_uuids_names(product_type, period, names)
        for uuid, _ in uuids_names:
            url = urljoin(self.web.url_dhus, f"odata/v1/Products('{uuid}')/Online/$value")
            r = s.get(url)
            if r.ok and (r.content == b'false'):
                logging.info(f'{_} offline')
                db.set_offline(product_type, uuid)

    def is_available(self):
        # for alternative links Online is not an option, but sometimes 500 is returned
        pass

    def set_on_daac(self, product_type, period=None, names=None):
        db = Database(self.db_path)
        s = requests.Session()
        s.headers = HEADERS
        s.headers['Authorization'] = f'Bearer {self.web.api_key_daac}'
        uuids_names = db.select_uuids_names(product_type, period, names)
        for uuid, name in uuids_names:
            url = make_url_daac(name, self.web.url_daac)
            logging.info(f'Checking if {name} is on DAAC')
            if s.head(url).ok:
                db.set_on_daac(product_type, uuid)

    def set_loaded(self, product_type, load_dir=None):
        db = Database(self.db_path)
        if load_dir is None:
            load_dir = product_type
        for s3path in Path(load_dir).glob('*.SEN3'):
            product_name = s3path.name.replace('.SEN3', '')
            db.set_loaded(product_name, product_type)
