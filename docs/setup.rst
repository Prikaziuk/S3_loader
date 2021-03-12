Step 0. set up
================

Required
----------

This code does requests to Copernicus Open Access Data Hub Service (DHUS) which requires authorization.
To be able to do anything with it you have to register on https://scihub.copernicus.eu/dhus/#/home
and **replace AUTH = ('DHUS_username', 'DHUS_password') in** ``S3_loader/config.py`` **with that credentials**.

An alternative NASA mirror is used to download offline (LTA) products unavailable on DHUS.
It also requires registration on https://ladsweb.modaps.eosdis.nasa.gov/profile/#app-keys
and **replacement of DAAC_API_KEY = 'DAAC-API-KEY' in** ``S3_loader/config.py`` **with that api key**.

Optional
---------

For pixel extraction
    - Sentinel Application Platform (SNAP) with Sentinel-3 toolbox is required http://step.esa.int/main/download/snap-download/
    - shapely package (for Windows from wheel is recommended) https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely

All operations require database connection, to view the SQLite database with GUI and export tables as csv you may use https://sqlitebrowser.org

.. code-block:: Python

    from S3_loader import S3Loader
    api = S3Loader(db_path=DATABASE_PATH)
