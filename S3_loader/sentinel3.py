import logging
from collections import namedtuple
from pathlib import Path

from . import config
from .checker import parse_point, parse_period, check_product_type, check_point_in_db, parse_names
from .database import Database
from .download import download_parallel
from .query import find_images

Web = namedtuple('Web', ['url_query', 'auth_query', 'url_dhus', 'auth_dhus', 'url_daac', 'api_key_daac'])


class S3Loader:
    URL_QUERY = 'https://scihub.copernicus.eu/dhus/search'
    # URL download
    URL_DHUS = 'https://scihub.copernicus.eu/dhus/odata/v1/'
    URL_DAAC = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/'

    def __init__(self, db_path):
        self.db_path = db_path
        self.web = Web(url_query=self.URL_QUERY, auth_query=config.AUTH,
                       url_dhus=self.URL_DHUS, auth_dhus=config.AUTH,
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

    def download(self, product_type, load_dir=None, names=None, period=None, parallel=False):
        check_product_type(product_type)
        if period is not None:
            period = parse_period(period)
        if names is not None:
            names = parse_names(names)

        db = Database(self.db_path)
        uuids_names = db.select_uuids_names(product_type, period, names)
        db.close()
        if len(uuids_names) == 0:
            err_msg = f'no products found in the database table {product_type} (==product type)'
            if period is not None:
                err_msg += f' for the period {period}'
            if names is not None:
                err_msg += f', names did not match any of the {len(names)} product names provided'
            raise Exception(err_msg)
        logging.info(f'Found {len(uuids_names)} products to download. Expected different number - redo the query')

        if load_dir is None:
            load_dir = product_type
        load_dir = Path(load_dir)
        load_dir.mkdir(exist_ok=True, parents=True)
        logging.info(f'Images will be downloaded to {load_dir}')

        download_parallel(uuids_names, load_dir, self.web, parallel=parallel)

    def is_online(self):
        pass

    def is_on_daac(self):
        pass
