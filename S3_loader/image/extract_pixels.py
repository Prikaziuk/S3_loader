import logging
import os
import subprocess

from S3_loader.image.utils import intersects

logging.basicConfig(level=logging.INFO)


def extract_dir(load_dir, point, out_dir, graph_path, site_name='test'):
    assert os.path.exists(graph_path), f'extraction .xml not found at {graph_path}'
    lat, lon = point
    sources = [os.path.join(load_dir, x) for x in os.listdir(load_dir)
               if intersects(os.path.join(load_dir, x), lat, lon)]
    if len(sources) == 0:
        logging.info(f'No intersection for {site_name}')
        return
    sources = ', '.join(sources)
    os.makedirs(out_dir, exist_ok=True)
    log = os.path.join(out_dir, f'{site_name}.log')
    with open(log, 'wb') as out:
        subprocess.call(['gpt', graph_path,
                         '-Psources=' + sources,
                         '-Psite=' + site_name,
                         '-Plat=' + str(lat),
                         '-Plon=' + str(lon),
                         '-Poutdir=' + out_dir],
                        stdout=out, stderr=out)
