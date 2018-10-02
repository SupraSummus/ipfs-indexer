import urllib.parse
from functools import lru_cache

from .ipfs import IPFSBacked


def KV(value_type):
    class __KV(IPFSBacked):
        """Map-like object that holds mutable mapping bytestring -> ipfs object."""
        CHILD_LINK_PREFIX = 'c'
        DATA_LINK_NAME = 'd'

        @classmethod
        def zero_state_hash(cls, backend):
            return backend.object_new()['Hash']

        def set(self, key, value):
            assert isinstance(key, bytes)
            assert isinstance(value, value_type)

            if len(key) == 0:
                if value.is_zero:
                    new_state_hash = self.backend.object_patch_rm_link(
                        self.state_hash, self.DATA_LINK_NAME,
                    )['Hash']
                else:
                    new_state_hash = self.backend.object_patch_add_link(
                        self.state_hash, self.DATA_LINK_NAME, value.state_hash,
                    )['Hash']

            else:
                links = self.__object_links
                key_part = self.__escape_key(key[0:1])

                if key_part in links:
                    child_hash = links[key_part]
                else:
                    child_hash = self.zero_state_hash(self.backend)

                child_hash = self.make_self(child_hash).set(key[1:], value).state_hash

                if child_hash == self.zero_state_hash(self.backend):
                    new_state_hash = self.backend.object_patch_rm_link(
                        self.state_hash,
                        key_part,
                    )['Hash']
                else:
                    new_state_hash = self.backend.object_patch_add_link(
                        self.state_hash,
                        key_part,
                        child_hash,
                    )['Hash']

            return self.make_self(new_state_hash)

        @property
        @lru_cache(maxsize=1024)
        def __object_links(self):
            return {
                link['Name']: link['Hash']
                for link in self.backend.object_links(self.state_hash).get('Links', [])
            }

        @classmethod
        def __escape_key(cls, key):
            return cls.CHILD_LINK_PREFIX + urllib.parse.quote_from_bytes(key, safe=' ')

        @classmethod
        def __unescape_key(cls, key):
            assert key.startswith(cls.CHILD_LINK_PREFIX)
            return urllib.parse.unquote_to_bytes(key[len(cls.CHILD_LINK_PREFIX):])

        def get(self, key):
            links = self.__object_links
            if len(key) == 0:
                return self.make(
                    value_type,
                    links.get(self.DATA_LINK_NAME),
                )
            elif self.__escape_key(key[0:1]) not in links:
                return None
            else:
                return self.make_self(
                    links[self.__escape_key(key[0:1])],
                ).get(key[1:])

        def keys(self, start=b''):
            links = self.__object_links
            if b'' >= start and self.DATA_LINK_NAME in links:
                yield b''
            for k in sorted(links.keys()):
                if not k.startswith(self.CHILD_LINK_PREFIX):
                    continue
                prefix = self.__unescape_key(k)
                if prefix >= start[:len(prefix)]:
                    for sk in self.make_self(
                        links[k],
                    ).keys(start[len(prefix):]):
                        yield prefix + sk

    return __KV


### Following code is outdated and i probably shuld nuke it but..


if __name__ == '__main__':
    import ipfsapi
    import sys

    if len(sys.argv) < 2 or sys.argv[1] not in ['empty', 'get', 'set']:
        print('usage: {} empty|get|set [STATE_HASH KEY]'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == 'empty':
        kv = KV(
            ipfs_api=ipfsapi.Client(),
        )
        print(kv.state_hash)
        sys.exit(0)

    kv = KV(
        state_hash=sys.argv[2],
        ipfs_api=ipfsapi.Client(),
    )
    key = sys.argv[3].encode('utf8')

    if sys.argv[1] == 'get':
        val = kv.get(key)
        if val is not None:
            sys.stdout.buffer.write(val)

    elif sys.argv[1] == 'set':
        kv.set(key, sys.stdin.buffer.read())
        print(kv.state_hash)

    else:
        assert False

    sys.exit(0)
