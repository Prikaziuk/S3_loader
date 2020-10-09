import logging
import subprocess
from functools import partial
from multiprocessing import Pool
from pathlib import Path

from S3_loader.image.utils import intersects

logging.basicConfig(level=logging.INFO)


def extract_dir(load_dir, point, out_dir, graph_path=None, filename='test'):
    if graph_path is None:
        graph_path = Path(__file__).parent / 'extract.xml'
    assert Path(graph_path).exists(), f'extraction .xml not found at {graph_path}'
    sources_lst = [x.as_posix() for x in Path(load_dir).glob('*') if intersects(x, point)]
    if len(sources_lst) == 0:
        logging.info(f'No intersection for {filename}')
        return
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if len(sources_lst) > 100:
        n_batches = 10
        sources_batch = chunks(sources_lst, n_batches)
        batches = [(f'{filename}_{i}', batch) for i, batch in enumerate(sources_batch)]
        with Pool(n_batches) as p:
            p.map(partial(extract, point=point, out_dir=out_dir, graph_path=graph_path), batches)
    else:
        extract((filename, sources_lst), point, out_dir, graph_path)


def extract(batch, point, out_dir, graph_path):
    extraction_fname, sources_lst = batch
    logging.info('Starting SNAP gpt for extraction')
    lat, lon = point
    with open(Path(out_dir, f'{extraction_fname}.log'), 'wb') as out:
        subprocess.call(['gpt', str(graph_path),
                         f'-Psources={", ".join(sources_lst)}',
                         f'-Psite={extraction_fname}',
                         f'-Plat={lat}',
                         f'-Plon={lon}',
                         f'-Poutdir={out_dir}'],
                        stdout=out, stderr=out)
    logging.info(f'Successfully extracted {point} to {out_dir}')


def chunks(lst, n):
    """
    Yield n number of striped chunks from lst
    function from https://stackoverflow.com/a/54802737 by Jurgen Strydom
    """
    for i in range(0, n):
        yield lst[i::n]
