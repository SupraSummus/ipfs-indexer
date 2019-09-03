import json

import requests

from go_ipfs_log_scraper import many, key_if_present, LOG_URL


if __name__ == '__main__':
    handler = many([
        key_if_present('peerID', print),
        key_if_present('peer', print),
    ])

    for line in requests.get(LOG_URL, stream=True).iter_lines():
        handler(json.loads(line))
