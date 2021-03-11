Step 3: extract pixels
============================

For this operation Sentinel Application Platform (SNAP) with Sentinel-3 toolbox is required http://step.esa.int/main/download/snap-download/

We use SNAP graph processing tool (gpt) from command line / terminal.

The xml-graphs used by gpt are located in ``S3_loader/image``, the default graph is ``extract.xml``

.. code-block:: Python

    from S3_loader.image.extract_pixels import extract_dir

    load_dir = 'example'
    out_dir = 'example_extracted'
    extract_dir(load_dir, POINT, out_dir, filename='prefix')

Will produce the standard SNAP Pixels extraction tool files in ``out_dir``

**prefix_OL_1_EFR_measurements.txt** - with band values per POINT

**prefix_productIdMap.txt** - with system location (names) of products

.. Note::

    The code will run in parallel (multiprocessing.Pool(5)) if there are more than 100 products, the files will be named
    prefix_0_0, prefix_0_1...



