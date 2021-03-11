Step 1: query for products
============================

Establish the database connection

.. code-block:: Python

    from S3_loader import S3Loader
    api = S3Loader(db_path=DATABASE_PATH)


Define parameters

.. code-block:: Python

    PRODUCT_TYPE = 'OL_1_EFR___'
    POINT = (52.251185, 5.690051)  # (latitude, longitude)
    PERIOD = ('2021-01-19', '2021-02-13')

Available product types

.. code-block:: Python

    PRODUCT_TYPES = [
        'SR_1_SRA___', 'SR_1_SRA_A', 'SR_1_SRA_BS', 'SR_2_LAN___',
        'OL_1_EFR___', 'OL_1_ERR___', 'OL_2_LFR___', 'OL_2_LRR___',
        'SL_1_RBT___', 'SL_2_LST___',
        'SY_2_SYN___', 'SY_2_V10___', 'SY_2_VG1___', 'SY_2_VGP___'
    ]

Query

.. code-block:: Python

    api.query(PRODUCT_TYPE, PERIOD, POINT)

This will create a table named ``PRODUCT_TYPE`` (OL_1_EFR___ in this example) in the local database (``DATABASE_PATH``) and fill it with product name, product uuid (needed for download), product sizes...

You will be able to estimate the time and space needed for further download.

.. Warning::
    One point - one database

    One database - many products (OLCI, SLSTR, Synergy, SRA)

    We query only for "Non Time Critical" products (can be adjusted in Sentinel-3/query.py L38)

**Additional queries**

Check if the product is offline (in long term archive, LTA)

.. code-block:: Python

    api.set_offline(PRODUCT_TYPE)

Check if the product is available at LAADS DAAC (api key for DAAC is required)

.. code-block:: Python

    api.set_on_daac(PRODUCT_TYPE) # very slow`


Set the state to loaded => will not be downloaded again

.. code-block:: Python

    load_dir = 'example'
    api.set_loaded(PRODUCT_TYPE, load_dir='example')

