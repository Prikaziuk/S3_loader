import os
import requests
import time

import logging
# # if you want to control logs uncomment all lines
# import sys
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # default logging.WARNING
logger = logging.getLogger()


TRY_RECONNECT = 3
REQUEST_TIMEOUT = 5
SLEEP_NOT_OK = 1800
DOWNLOAD_TIMEOUT = 900
SEC_2_MIN = 1 / 60


def get_request(url, auth, tmp_path=None, headers=None):
    start_f = time.time()
    loaded = None
    tried = 0
    while tried < TRY_RECONNECT:
        tried += 1
        logger.debug('Connecting... attempt # {}'.format(tried))
        timeout = False
        start = time.time()
        try:
            if headers is None:  # because query or md5 were asked
                r = requests.get(url, auth=auth, stream=True, timeout=REQUEST_TIMEOUT)
            else:
                r = requests.get(url, headers=headers, stream=True, timeout=REQUEST_TIMEOUT)
            if not r.ok:
                if r.status_code == 401:
                    logger.critical('401 UNAUTHORIZED. Did you provide valid credentials in -a parameter?')
                    exit(-1)
                if r.status_code == 500:
                    logger.critical('Internal server error. Rethrowing is useless')
                    return loaded, tried
                if r.status_code in (403, 404):
                    logger.critical('404: Rethrowing is useless')
                    return loaded, tried
                logger.warning('Status code {}. Sleeping for SLEEP_NOT_OK time {}s'.format(r.status_code, SLEEP_NOT_OK))
                time.sleep(SLEEP_NOT_OK)
                continue
            if tmp_path is not None:
                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                with open(tmp_path, 'wb') as tmp:
                    for chunk in r.iter_content(chunk_size=1024):
                        # if chunk:  # filter out keep-alive new chunks
                        tmp.write(chunk)
                        if time.time() - start > DOWNLOAD_TIMEOUT:
                            r.close()
                            logger.warning('Custom timeout on download {}'.format(tried))
                            timeout = True
                            break
        except Exception as e:  # may be (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
            passed = time.time() - start
            logger.warning('Exception: {}; {} seconds passed, retrying...'.
                           format(e.__class__, passed))
            # time.sleep(SLEEP)  # time to maybe restore the connection
            continue  # this is needed because timeout==False in case of exceptions

        if tmp_path is None:
            loaded = r.content
            r.close()
            break
        else:
            if not timeout:
                with open(tmp_path, 'rb') as tmp:
                    loaded = tmp.read()
                    break

    elapsed = round(time.time() - start_f, 2)
    logger.debug('Elapsed \t{}\t min\n'.format(elapsed * SEC_2_MIN))
    return loaded, tried
