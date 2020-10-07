"""
main function of Sentinel-3 load package

Input:

required:
    product_type:
        SR_1_SRA___, SR_1_SRA_A, SR_1_SRA_BS, SR_2_LAN___,
        OL_1_EFR___, OL_1_ERR___, OL_2_LFR___, OL_2_LRR___,
        SL_1_RBT___, SL_2_LST___,
        SY_2_SYN___, SY_2_V10___, SY_2_VG1___, SY_2_VGP___

    period: (start_date, end_date) %Y-%m-%d
    point: (lat, lon)

optional:
    database_path: str
    load_dir_path: str


(c) Prikaziuk 2020, prikaziuk@gmail.com
"""
import json
import logging

from pathlib import Path

from S3_loader.checker import check_product_type, parse_period, parse_point, check_point_in_db
from S3_loader.database import Database
from S3_loader.query import find_images
from S3_loader.download import download_parallel


logging.basicConfig(level=logging.INFO)

with open('../.config', 'r') as json_file:
    CONFIG = json.load(json_file)
AUTH = (CONFIG['DHUS_USERNAME'], CONFIG['DHUS_PASSWORD'])


def images2db(images, product_type, point, database_path):
    db = Database(database_path)
    db.create_points_table()
    db.insert_point(point)
    db.create_products_table(product_type)
    images['point_id'] = [db.get_point_id(point)] * images['n_images']
    db.insert_images(images, product_type)
    db.conn.close()
    logging.info(f'Images successfully inserted into {product_type} table of {database_path}')


def download(product_type, period, point, database_path, load_dir_path=None):
    if not Path(database_path).is_file():
        logging.info(f'No database file has been found, querying and creating one')
        images = find_images(product_type, period, point, AUTH)
        images2db(images, product_type, point, database_path)

    db = Database(database_path)
    uuids_names = db.select_uuids_names(product_type, period)
    if len(uuids_names) == 0:
        logging.info(f'no products to download have been found in the database {database_path} ' +
                     f'for specified product type {product_type}, period {period}' + '\n' +
                     'Querying Copernicus to see if they exist at all...')
        images = find_images(product_type, period, point, AUTH)
        images2db(images, product_type, point, database_path)

        uuids_names = db.select_uuids_names(product_type, period)
        assert len(uuids_names) != 0, \
            f'no products found in the database for specified product type {product_type}, period {period}'

    if load_dir_path is None:
        load_dir_path = Path('..', product_type)
    load_dir_path = Path(load_dir_path)
    load_dir_path.mkdir(exist_ok=True, parents=True)

    # TODO names are not unique +/- 1 second etc, ask the user which to load
    download_parallel(uuids_names, load_dir_path,
                      auth=AUTH, api_key=CONFIG['DAAC_API_KEY'], parallel=False)
    # TODO database add-ons: set loaded, set online
    db.conn.close()


if __name__ == '__main__':
    PRODUCT_TYPE = 'OL_1_EFR___'
    PERIOD = ('2020-08-01', '2020-08-10')
    POINT = (56.46, 7.57)
    DATABASE_PATH = '../test.db'

    check_product_type(PRODUCT_TYPE)
    PERIOD = parse_period(PERIOD)
    POINT = parse_point(POINT)
    check_point_in_db(DATABASE_PATH, POINT)

    images_dict = find_images(product_type=PRODUCT_TYPE, period=PERIOD, point=POINT, auth=AUTH)
    images2db(images=images_dict, product_type=PRODUCT_TYPE, point=POINT, database_path=DATABASE_PATH)
    # download(PRODUCT_TYPE, PERIOD, POINT, DATABASE_PATH)
