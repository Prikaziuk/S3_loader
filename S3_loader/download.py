import hashlib
import io
import logging
import zipfile
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
from urllib.parse import urljoin

from .get_request import get_request

# if you want to control logs uncomment these lines
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # default logging.WARNING
logger = logging.getLogger()

URL_DHUS = 'https://scihub.copernicus.eu/dhus/'
URL_DAAC = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/450/'


def download_parallel(uuids_names, load_dir_path, web, parallel=False):
    tmp_path1 = load_dir_path / 'tmp'
    tmp_path2 = load_dir_path / 'tmp2'
    if parallel:
        for i, pair in enumerate(chunks_of_n(uuids_names, 2)):
            logger.info(f'{(i + 1) * 2} / {len(uuids_names)}')
            if len(pair) == 2:
                (uuid1, name1), (uuid2, name2) = pair
                with Pool(2) as p:
                    p.starmap(download_single_product, [(uuid1, name1, load_dir_path, tmp_path1, web),
                                                        (uuid2, name2, load_dir_path, tmp_path2, web)])
            else:
                uuid, name = pair
                download_single_product(uuid, name, load_dir_path, tmp_path1, web)
    else:
        for i, (uuid, name) in enumerate(uuids_names):
            logger.info(f'{i} / {len(uuids_names)}')
            download_single_product(uuid, name, load_dir_path, tmp_path1, web)


def download_single_product(uuid, name, load_dir_path, tmp_path, web):
    loaded = False
    if Path(load_dir_path, name+'.SEN3').is_dir():
        logger.info(f'Product {name}.SEN3 has already been downloaded to {load_dir_path}')
        loaded = True
        return loaded
    online = is_online(uuid, web.auth_dhus, web.url_dhus)
    content, tried = None, None
    if online or (online is None):
        logger.info(f'Started downloading {name} from DHUS')
        url = urljoin(web.url_dhus, f"odata/v1/Products('{uuid}')/$value")
        content, tried = get_request(url, web.auth_dhus, tmp_path)
    if (online is False) or (content is None):
        if online is False:
            logger.warning(f'Product {name} is offline in ESA Long term archive LTA')
        if web.api_key_daac:
            logger.info(f'Started downloading {name} from DAAC')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                              'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                              'Chrome/70.0.3538.77 ' +
                              'Safari/537.36 ' +
                              'Edg/79.0.309.43',
                'Authorization': f'Bearer {web.api_key_daac}'
            }
            url = make_url_daac(name, web.url_daac)
            content, tried = get_request(url, auth=None, tmp_path=tmp_path, headers=headers)
        else:
            logger.warning('DAAC API key was not provided, can not use the alternative DAAC mirror ' +
                           f'to download the offline {name} product')
            return loaded
    if Path(tmp_path).exists():
        Path(tmp_path).unlink()
    if content is None:
        logger.error(f'Was not able to download the product {name} after {tried} attempts')
        return loaded
    if not is_md5_ok(content, uuid, web.auth_dhus, web.url_dhus):
        # checksums should be equal in both cases, we receive the same data
        logger.error(f'MD5 sums were not equal for {name}, the product is not downloaded')
        return loaded
    z = zipfile.ZipFile(io.BytesIO(content))
    z.extractall(load_dir_path)
    logger.info(f'SUCCESSFULLY UNZIPPED AND SAVED \n {name}.SEN3 in {load_dir_path}')
    loaded = True
    return loaded


def is_online(uuid, auth, url_dhus):
    online = None
    url = urljoin(url_dhus, f"odata/v1/Products('{uuid}')/Online/$value")
    res, _ = get_request(url, auth)
    if res is not None:
        online = (res == b'true')
    return online


def make_url_daac(name, url_daac=URL_DAAC):
    # '450/S3A_OL_1_EFR/2018/244/S3A_OL_1_EFR____20180901T103822_20180901T104122_20180902T154621_0179_035_165_2340_LN1_O_NT_002.zip'
    product_type = name[:12]
    date = datetime.strptime(name[16:31], '%Y%m%dT%H%M%S')
    year = date.strftime('%Y')
    doy = date.strftime('%j')
    return urljoin(url_daac, '/'.join([product_type, year, doy, name+'.zip']))


def is_md5_ok(content, uuid, auth, url_dhus):
    if content is None:
        return False

    url = urljoin(url_dhus, f"odata/v1/Products('{uuid}')/Checksum/Value/$value")
    md5_content, tried = get_request(url, auth)
    if md5_content is None:
        logger.warning(f'MD5 sums were not downloaded after {tried} attempts')
        return False

    loaded_md5 = hashlib.md5(content).hexdigest()
    expected_md5 = md5_content.decode('utf-8').lower()
    return loaded_md5 == expected_md5


def chunks_of_n(lst, n):
    """
    Yield successive n-sized chunks from lst.
    function from https://stackoverflow.com/a/312464 by Ned Batchelder
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
