import urllib.parse


class KV:
    """Map-like object that holds mutable mapping bytestring -> ipfs object hash."""
    INITIAL_NODE_HASH = 'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'
    CHILD_LINK_PREFIX = 'c'
    DATA_LINK_NAME = 'd'

    def __init__(self, ipfs_api, state_hash=INITIAL_NODE_HASH, segmenting=None):
        """
        `state_hash` - IPFS hash of KVstore state
        `segmenting` - iterable returning byte counts for path segment lengths
        """
        if segmenting is None:
            def segmenting(_):
                return 2

        self.__state_hash = state_hash
        self.__segmenting = segmenting
        self.__ipfs_api = ipfs_api

    @property
    def state_hash(self):
        return self.__state_hash

    def set(self, key, value):
        self.__state_hash = self.__set(
            self.__state_hash,
            self.__split_key(key), value,
        )

    def __set(self, parent_hash, key_parts, value):
        if len(key_parts) == 0:
            if value is None:
                return self.__ipfs_api.object_patch_rm_link(parent_hash, self.DATA_LINK_NAME)['Hash']
            else:
                return self.__ipfs_api.object_patch_add_link(parent_hash, self.DATA_LINK_NAME, value)['Hash']

        else:
            key_part = key_parts[0]

            links = self.__object_links(parent_hash)
            if key_part in links:
                next_parent_hash = links[key_part]
            else:
                next_parent_hash = self.INITIAL_NODE_HASH

            next_parent_hash = self.__set(next_parent_hash, key_parts[1:], value)
            if next_parent_hash == self.INITIAL_NODE_HASH:
                return self.__ipfs_api.object_patch_rm_link(
                    parent_hash,
                    key_part,
                )['Hash']
            else:
                return self.__ipfs_api.object_patch_add_link(
                    parent_hash,
                    key_part,
                    next_parent_hash,
                )['Hash']

    def __object_links(self, root):
        return {
            link['Name']: link['Hash']
            for link in self.__ipfs_api.object_links(root).get('Links', [])
        }

    def __escape_key(self, key):
        return urllib.parse.quote_from_bytes(key, safe=' ')

    def __unescape_key(self, key):
        return urllib.parse.unquote_to_bytes(key)

    def __split_key(self, key):
        parts = []
        i = 0
        while len(key) != 0:
            part_len = self.__segmenting(i)
            if part_len is None:
                parts.append(self.CHILD_LINK_PREFIX + self.__escape_key(key))
                break
            if part_len > 0:
                parts.append(self.CHILD_LINK_PREFIX + self.__escape_key(key[:part_len]))
                key = key[part_len:]
                i += 1
            else:
                assert False, "key segmenting function must return positive int or None"
        return parts

    def get(self, key):
        root = self.__state_hash
        links = self.__object_links(root)
        for key_part in self.__split_key(key):
            if key_part not in links:
                return None
            root = links[key_part]
            links = self.__object_links(root)
        return links.get(self.DATA_LINK_NAME)

    def keys(self, start=b''):
        for k in self.__keys(self.__state_hash, start, b''):
            yield k

    def __keys(self, root, start, prefix):
        links = self.__object_links(root)
        if prefix >= start and self.DATA_LINK_NAME in links:
            yield prefix
        for k in sorted(links.keys()):
            new_prefix = prefix + self.__unescape_key(k[len(self.CHILD_LINK_PREFIX):])
            if new_prefix >= start[:len(new_prefix)]:
                for sk in self.__keys(links[k], start, new_prefix):
                    yield sk

    def merge(self, other_root, merge_func=lambda a, b: b):
        raise NotImplementedError()


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
