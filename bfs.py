import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import subprocess
import logging
import time


logger = logging.getLogger(__name__)


# visited vertices
visited = set()
visited_lock = threading.Lock()


working_count = 0
working_count_lock = threading.Lock()


def decrease_working_count():
    global working_count
    with working_count_lock:
        working_count -= 1


def increase_working_count():
    global working_count
    with working_count_lock:
        working_count += 1


def process_vertice(v):
    increase_working_count()

    with visited_lock:
        if v in visited:
            # skip visited
            return
        else:
            # reserve this vertice for this worker
            visited.add(v)
            sys.stdout.write(f'{v}\n')
            sys.stdout.flush()

    logger.debug('start %s', v)

    r = subprocess.run([
        'bash', '-c',
        f'ipfs dht query -- {v} | head -n64',
    ], capture_output=True, check=True)

    if r.returncode != 0:
        logger.error('code %s: %d', v, r.returncode)

    if r.stderr:
        logger.error('stderr %s: %s', v, r.stderr)

    for line in r.stdout.decode('ascii').split('\n'):
        if line != '':
            queue_vertice(line)


executor = ThreadPoolExecutor(max_workers=16)


def check_exception(f):
    exc = f.exception()
    if exc is not None:
        logger.error('got exception', exc)


def queue_vertice(v):
    assert(isinstance(v, str))

    with visited_lock:
        if v in visited:
            return

    logger.debug('queuing %s', v)

    future = executor.submit(process_vertice, v)
    future.add_done_callback(check_exception)
    future.add_done_callback(lambda f: decrease_working_count())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    futures = []

    # load start vertices
    for line in sys.stdin:
        if line[-1] == '\n':
            line = line[:-1]
        queue_vertice(line)

    while True:
        with working_count_lock:
            wc = working_count
        with visited_lock:
            vc = len(visited)
        logger.info(
            '#visited = %d, #todo = %d, #in progress = %d',
            vc,
            executor._work_queue.qsize(),
            wc,
        )
        time.sleep(10)
