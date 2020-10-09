import logging
import subprocess
from pathlib import Path

from S3_loader.image.utils import intersects

logging.basicConfig(level=logging.INFO)


def extract_dir(load_dir, point, out_dir, graph_path=None, site_name='test'):
    if graph_path is None:
        graph_path = (Path(__file__).parent / 'extract.xml').as_posix()
    assert Path(graph_path).exists(), f'extraction .xml not found at {graph_path}'
    lat, lon = point
    sources = [x.as_posix() for x in Path(load_dir).glob('*') if intersects(x, lat, lon)]
    if len(sources) == 0:
        logging.info(f'No intersection for {site_name}')
        return
    sources_str = ', '.join(sources)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    logging.info('Starting SNAP gpt for extraction')
    with open(Path(out_dir, f'{site_name}.log'), 'wb') as out:
        subprocess.call(['gpt', graph_path,
                         f'-Psources={sources_str}',
                         f'-Psite={site_name}',
                         f'-Plat={lat}',
                         f'-Plon={lon}',
                         f'-Poutdir={out_dir}'],
                        stdout=out, stderr=out)
    logging.info(f'Successfully extracted {point} to {out_dir}')
