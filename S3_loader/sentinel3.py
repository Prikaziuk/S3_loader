import logging

from S3_loader import config
from S3_loader.database import Database
from S3_loader.query import find_images
from .checker import parse_point, parse_period, check_product_type, check_point_in_db


class S3Loader:
    URL_QUERY = 'https://scihub.copernicus.eu/dhus/search'
    # URL download
    URL_DHUS = 'https://scihub.copernicus.eu/dhus/odata/v1/'
    URL_DAAC = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/'

    def __init__(self):
        self.auth = config.AUTH
        self.api_key = config.DAAC_API_KEY
        self.images = dict()

    def query(self, product_type, period, point):
        check_product_type(product_type)
        period = parse_period(period)
        point = parse_point(point)
        self.images = find_images(product_type, period, point, self.auth, self.URL_QUERY)

    def images2db(self, db_path):
        if len(self.images) == 0:
            raise Exception(f'Do not see any images, please, launch the query first: `S3Loader.query()`')

        point = self.images['point']
        check_point_in_db(db_path, point)

        product_type = self.images['product_type']
        db = Database(db_path)
        db.create_points_table()
        db.insert_point(point)
        db.create_products_table(product_type)
        self.images['point_id'] = [db.get_point_id(point)] * self.images['n_images']
        db.insert_images(self.images, product_type)
        db.conn.close()
        logging.info(f'Images successfully inserted into {product_type} table of {db_path}')
