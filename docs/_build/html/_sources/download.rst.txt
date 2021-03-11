Step 2: download
==================

When the database is filled (see Step 1) you can select products from it to download.

Establish the database connection

.. code-block:: Python

    from S3_loader import S3Loader
    api = S3Loader(db_path=DATABASE_PATH)

There are various options to select products from database for download.

1. By dates

.. code-block:: Python

    load_dir = 'example'  # [optional] if None => load_dir == product_type
    period = ('2021-01-25', '2021-01-26')  # notice this is one day: 25th of January 2021
    api.download(PRODUCT_TYPE, load_dir=load_dir, period=period)

2. By names

.. code-block:: Python

    names = ['S3A_OL_1_EFR____20210212T102851_20210212T103151_20210213T155710_0179_068_222_1980_LN1_O_NT_002']
    api.download(PRODUCT_TYPE, names=names)

3. Only the frequent orbits (~27 products). May be used to augment Google Earth Engine dataset for observation angles

.. code-block:: Python

    api.download(PRODUCT_TYPE, orbits=True)

4. All products in the database (better in parallel)

.. code-block:: Python

    api.download(PRODUCT_TYPE, parallel=True)


Once the download is completed, it is a good idea to set loaded = 1 in the database to avoid downloading it again

.. code-block:: Python

    load_dir = 'example'
    api.set_loaded(PRODUCT_TYPE, load_dir='example')

Long Therm Archive (LTA)
-------------------------

We found an alternative source of OLCI level-1 products - LDAAC.

They also have SLSTR level-1, feel free to change the DHUS_URL and enjoy.
