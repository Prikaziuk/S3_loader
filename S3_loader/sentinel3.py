import logging

from . import config
from .database import Database
from .query import find_images
from .checker import parse_point, parse_period, check_product_type, check_point_in_db


class S3Loader:
    URL_QUERY = 'https://scihub.copernicus.eu/dhus/search'
    # URL download
    URL_DHUS = 'https://scihub.copernicus.eu/dhus/odata/v1/'
    URL_DAAC = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/'

    def __init__(self, db_path):
        self.db_path = db_path
        self.db = Database(db_path)
        self.auth = config.AUTH
        self.api_key = config.DAAC_API_KEY

    def query(self, product_type, period, point):
        check_product_type(product_type)
        period = parse_period(period)
        point = parse_point(point)
        check_point_in_db(self.db, point)
        images = find_images(product_type, period, point, self.auth, self.URL_QUERY)
        self._images2db(images)

    def _images2db(self, images):
        point = images['point']
        product_type = images['product_type']
        self.db.create_points_table()
        self.db.insert_point(point)
        self.db.create_products_table(product_type)
        images['point_id'] = [self.db.get_point_id(point)] * images['n_images']
        self.db.insert_images(images, product_type)
        logging.info(f'Images successfully inserted into {product_type} table of {self.db_path}')

    def _download(self):
        pass

    def download_names(self, names, db_path=None):
        pass

    def download_period(self, period, db_path=None):
        pass
