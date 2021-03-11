import logging
import subprocess
from functools import partial
from multiprocessing import Pool
from pathlib import Path

from S3_loader.image.utils import intersects
from S3_loader.checker import parse_point

logging.basicConfig(level=logging.INFO)


def extract_dir(load_dir, point, out_dir, graph_path=None, filename='test'):
    point = parse_point(point)
    if graph_path is None:
        graph_path = Path(__file__).parent / 'extract.xml'
    assert Path(graph_path).exists(), f'extraction .xml not found at {graph_path}'
    if isinstance(load_dir, list):
        sources_lst = [Path(x).absolute().as_posix() for x in load_dir]
    else:
        sources_lst = [x.absolute().as_posix() for x in Path(load_dir).glob('*.SEN3') if intersects(x, point)]
    if len(sources_lst) == 0:
        logging.info(f'No intersection for {filename}')
        return
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if len(sources_lst) > 100:
        n_batches = 5
        for j, sources_batch in enumerate(n_chunks(sources_lst, n_batches)):
            n_processes = 5
            batches = [(f'{filename}_{j}_{i}', batch) for i, batch in enumerate(n_chunks(sources_batch, n_processes))]
            with Pool(n_processes) as p:
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


def n_chunks(lst, n):
    """
    Yield n number of striped chunks from lst
    function from https://stackoverflow.com/a/54802737 by Jurgen Strydom
    """
    for i in range(0, n):
        yield lst[i::n]
