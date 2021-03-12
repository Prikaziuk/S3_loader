from S3_loader import S3Loader


if __name__ == '__main__':

    """
    This code does requests to Copernicus Open Access Data Hub Service (DHUS) which requires authorization.
    To be able to do anything with it you have to register on https://scihub.copernicus.eu/dhus/#/home
    and replace AUTH = ('DHUS_username', 'DHUS_password') in `S3_loader/config.py` with that credentials.
    
    An alternative NASA mirror is used to download offline (LTA) products unavailable on DHUS.
    It also requires registration on https://ladsweb.modaps.eosdis.nasa.gov/profile/#app-keys
    and replacement of DAAC_API_KEY = 'DAAC-API-KEY' in `S3_loader/config.py` with that api key.
    """

    # LOCAL DATABASE CREATION
    DATABASE_PATH = 'example.db'
    api = S3Loader(db_path=DATABASE_PATH)

    # QUERY #################################################################
    # # basic use case - see what is on Copernicus DHUS for your point
    PRODUCT_TYPE = 'OL_1_EFR___'
    POINT = (52.251185, 5.690051)
    PERIOD = ('2021-01-19', '2021-02-13')
    api.query(PRODUCT_TYPE, PERIOD, POINT)

    # DOWNLOAD ##############################################################
    # # once the database is created - download
    load_dir = 'example'  # if None => load_dir == product_type
    # # 1. single day
    period = ('2021-01-25', '2021-01-26')
    api.download(PRODUCT_TYPE, load_dir=load_dir, period=period)

    # # 2. specific product
    names = ['S3A_OL_1_EFR____20210212T102851_20210212T103151_20210213T155710_0179_068_222_1980_LN1_O_NT_002']
    # api.download(PRODUCT_TYPE, names=names)

    # # 3. download only the frequent orbits (~27 products)
    # api.download(PRODUCT_TYPE, orbits=True)

    # # 4. all products in the database (better in parallel)
    # api.download(PRODUCT_TYPE, parallel=True)

    # EXTRA INFO TO DATABASE ###############################################
    # # check if the product is offline (in long term archive, LTA)
    # api.set_offline(PRODUCT_TYPE)

    # # check if the product is available at LAADS DAAC (api key for DAAC is required)
    # api.set_on_daac(PRODUCT_TYPE)  # very slow

    # # set the state to loaded => won't be downloaded again
    # load_dir = 'example'
    # api.set_loaded(PRODUCT_TYPE, load_dir)

    """
    SNAP BONUS
    extract pixels from the downloaded files 
    Required:
        - ESA SNAP with Sentinel-3 toolbox is required http://step.esa.int/main/download/snap-download/ 
        - shapely package (for Windows from wheel is recommended) https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
    """
    # from S3_loader.image.extract_pixels import extract_dir
    # load_dir = PRODUCT_TYPE
    # out_dir = 'example_extracted'
    # extract_dir(load_dir, POINT, out_dir, filename='example')
