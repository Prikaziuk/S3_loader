import logging
import subprocess

from pathlib import Path

from S3_loader.image.utils import make_polygon_wkt, intersects


def subset_slstr_cmd(products_in, subset_out, point, subset_graph, reader):
    """
    for SLSTR we have 2 iterations with slstr500 and slstr1000
    this is provided by two readers of SLSTR products which requires subsetting to .dim products
    :return: extracted path (sources)
    """
    lat, lon = point
    wkt4subset = make_polygon_wkt(lat, lon, km_shift=3)
    for file in Path(products_in).glob('*'):
        if intersects(file, lat, lon):
            log = subset_out.with_suffix('.log')
            with open(log, 'wb') as out:
                subprocess.call(['gpt', subset_graph,
                                 f'-Pinput={file.as_posix()}',
                                 f'-Preader={reader}',
                                 f'-Pwkt={wkt4subset}',
                                 f'-Poutfile={subset_out.with_suffix(".nc")}'],  # cutting .SEN3
                                stdout=out, stderr=out)
    logging.info(f'finished subsetting {reader}')
