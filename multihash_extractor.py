import sys
import re
from functools import lru_cache
import binascii

import multihash


@lru_cache(maxsize=1024*10)
def is_multihash(text):
    try:
        b = text.encode('ascii')
        multihash.decode(b, 'base58')
        return True
    except (ValueError, KeyError):
        return False


if __name__ == '__main__':
    """ Given input text stream (stdin) extracts all valid multihash strings and prints them to stdout. """
    pattern = re.compile('[a-zA-Z0-9]+')
    for line in sys.stdin:
        for text in pattern.findall(line):
            if is_multihash(text):
                print(text)
