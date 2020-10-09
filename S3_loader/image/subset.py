import logging
import os
import subprocess

from S3_loader.image.utils import make_polygon_wkt, intersects


def subset_slstr_cmd(products_in, subset_out, lat, lon, subset_graph, reader):
    """
    for SLSTR we have 2 iterations with slstr500 and slstr1000
    this is provided by two readers of SLSTR products which requires subsetting to .dim products
    :return: extracted path (sources)
    """
    wkt4subset = make_polygon_wkt(lat, lon, km_shift=3)
    for file in os.listdir(products_in):
        if intersects(os.path.join(products_in, file), lat, lon):
            log = os.path.join(os.path.dirname(subset_out), f'{os.path.basename(subset_out)}.log')
            with open(log, 'wb') as out:
                subprocess.call(['gpt', subset_graph,
                                 '-Pinput=' + os.path.join(products_in, file),
                                 '-Preader=' + reader,
                                 '-Pwkt=' + wkt4subset,
                                 '-Poutfile=' + os.path.join(subset_out, file[:-5] + '.nc')],  # cutting .SEN3
                                stdout=out, stderr=out)
    logging.info(f'finished subsetting {reader}')
