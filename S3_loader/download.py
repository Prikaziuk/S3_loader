import hashlib
import io
import logging
import zipfile
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

from S3_loader.get_request import get_request

# if you want to control logs uncomment these lines
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # default logging.WARNING
logger = logging.getLogger()

URL_DHUS = 'https://scihub.copernicus.eu/dhus/odata/v1/'
URL_DAAC = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/'


def download_parallel(uuids_names, load_dir_path, auth, api_key=None, parallel=False):
    tmp_path1 = load_dir_path / 'tmp'
    tmp_path2 = load_dir_path / 'tmp2'
    if parallel:
        for i, pair in enumerate(chunks(uuids_names, 2)):
            logger.info(f'{(i + 1) * 2} / {len(uuids_names)}')
            if len(pair) == 2:
                (uuid1, name1), (uuid2, name2) = pair
                with Pool(2) as p:
                    p.starmap(download_single_product, [(uuid1, name1, load_dir_path, tmp_path1, auth, api_key),
                                                        (uuid2, name2, load_dir_path, tmp_path2, auth, api_key)])
            else:
                uuid, name = pair
                download_single_product(uuid, name, load_dir_path, tmp_path1, auth, api_key)
    else:
        for i, (uuid, name) in enumerate(uuids_names):
            logger.info(f'{i} / {len(uuids_names)}')
            download_single_product(uuid, name, load_dir_path, tmp_path1, auth, api_key)


def download_single_product(uuid, name, load_dir_path, tmp_path, auth, api_key=None):
    loaded = False
    if Path(load_dir_path, name+'.SEN3').is_dir():
        logger.info(f'Product {name}.SEN3 has already been downloaded to {load_dir_path}')
        loaded = True
        return loaded
    if is_online(uuid, auth):
        logger.info(f'Started downloading {name} from DHUS')
        url = URL_DHUS + f"Products('{uuid}')/$value"
        content, tried = get_request(url, auth, tmp_path)
    else:
        logger.warning(f'Product {name} is offline in ESA Long term archive LTA')
        if api_key:
            logger.info(f'Started downloading {name} from DAAC')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                              'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                              'Chrome/70.0.3538.77 ' +
                              'Safari/537.36 ' +
                              'Edg/79.0.309.43',
                'Authorization': f'Bearer {api_key}'
            }
            url = make_url_daac(name)
            content, tried = get_request(url, auth=None, tmp_path=tmp_path, headers=headers)
        else:
            logger.warning('DAAC API key was not provided, can not use the alternative DAAC mirror ' +
                           f'to download the offline {name} product')
            return loaded
    if content is None:
        logger.error(f'Was not able to download the product {name} after {tried} attempts')
        return loaded
    if not is_md5_ok(content, uuid, auth):
        # checksums should be equal in both cases, we receive the same data
        logger.error(f'MD5 sums were not equal for {name}, the product is not downloaded')
        return loaded
    z = zipfile.ZipFile(io.BytesIO(content))
    z.extractall(load_dir_path)
    logger.info(f'SUCCESSFULLY UNZIPPED AND SAVED \n {name}.SEN3 in {load_dir_path}')
    loaded = True
    return loaded


def is_online(uuid, auth):
    online = False
    url = URL_DHUS + f"Products('{uuid}')/Online/$value"
    res, _ = get_request(url, auth)
    if res is not None:
        online = (res == b'true')
    return online


def make_url_daac(name):
    # '450/S3A_OL_1_EFR/2018/244/S3A_OL_1_EFR____20180901T103822_20180901T104122_20180902T154621_0179_035_165_2340_LN1_O_NT_002.zip'
    product_type = name[:12]
    date = datetime.strptime(name[16:31], '%Y%m%dT%H%M%S')
    year = date.strftime('%Y')
    doy = date.strftime('%j')
    return URL_DAAC + '/'.join([product_type, year, doy, name+'.zip'])


def is_md5_ok(content, uuid, auth):
    if content is None:
        return False

    url = URL_DHUS + f"Products('{uuid}')/Checksum/Value/$value"
    md5_content, tried = get_request(url, auth)
    if md5_content is None:
        logger.warning(f'MD5 sums were not downloaded after {tried} attempts')
        return False

    loaded_md5 = hashlib.md5(content).hexdigest()
    expected_md5 = md5_content.decode('utf-8').lower()
    return loaded_md5 == expected_md5


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    function from https://stackoverflow.com/a/312464 by Ned Batchelder
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
