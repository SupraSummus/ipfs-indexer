import urllib.parse


class KV:
    INITIAL_NODE_HASH = 'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'
    CHILD_LINK_PREFIX = '_'
    KEY_LENGTH_LINK_NAME = 'k'
    MAX_CHILDREN_COUNT = 256  # this musnt be less than 256
    MAX_KEY_LENGTH = 64

    def __init__(self, ipfs_client, state_hash):
        self.__state_hash = state_hash
        self.__ipfs_client = ipfs_client

    @property
    def state_hash(self):
        return self.__state_hash

    @property
    def __key_length(self):
        key_obj = self.__links.get(KEY_LENGTH_LINK_NAME)
        if key_obj is None:
            return self.MAX_KEY_LENGTH
        else:
            return int(self.__ipfs_client.get_object_data(key_obj))

    @property
    def __links(self):
        return {
            link['Name']: link['Hash']
            for link in self.__client.object_links(self.__root).get('Links', [])
        }

    @property
    def __children(self):
        return {
            self.__unescape_key(k): v
            for k, v in self.__links
            if k.startswith(CHILD_LINK_PREFIX)
        }

    def __escape_key(self, key):
        return KEY_LINK_PREFIX + urllib.parse.quote_from_bytes(key, safe=' ')

    def __unescape_key(self, key):
        assert key.startswith(KEY_LINK_PREFIX)
        return urllib.parse.unquote_to_bytes(key[len(KEY_LINK_PREFIX):])

def __normalized(client, root):
    children = _children(client, root)

    if len(children) == 0:
        return _INITIAL_NODE_HASH

    elif len(children) == 1 and __key_length(client, root) < MAX_KEY_LENGTH:
        key, child = children.items()[0]
        if len(key) < __key_length(client, root):
            # this only entry is a leaf
            return root
        return __normalized(client, prefix_keys(client, child, key))

    elif len(children) > MAX_CHILDREN_COUNT:
        # determine max prefix len so child count will be <= MAX_CHILDREN_COUNT
        for prefix_len in reversed(range(1, __key_length(client, root))):
            prefixes = set(k[:prefix_len] for k in __children(client, root))
            if len(prefixes) <= MAX_CHILDREN_COUNT:
                break

        new_root = INITIAL_NODE_HASH
        new_root = _set_link(client, new_root, KEY_LENGTH_LINK_NAME, client.object_patch_set_data(
            EMPTY_OBJECT, b'{}'.format(prefix_len),
        ))
        for k, v in __children(client, root):
            new_root = _set
        


def kv_empty(client):
    return _INITIAL_NODE_HASH


def kv_set(client, root, key, value):
    key_length = _key_length(client, root)

    if len(key) < key_length:
        if value is None:
            new_root = client.object_patch_rm_link(root, _escape_key(key))['Hash']
        else:
            new_root = client.object_patch_add_link(root, _escape_key(key), value)['Hash']

    else:
        key_head = _escape_key(key[:key_length])
        key_tail = key[key_length:]

        links = _links(client, root)
        if key_head in links:
            next_parent_hash = links[key_head]
        else:
            next_parent_hash = INITIAL_NODE_HASH

        next_parent_hash = kv_set(client, next_parent_hash, key_tail, value)
        if next_parent_hash == INITIAL_NODE_HASH:
            new_root = client.object_patch_rm_link(
                parent_hash,
                key_part,
            )['Hash']
        else:
            new_root = client.object_patch_add_link(
                parent_hash,
                key_part,
                next_parent_hash,
            )['Hash']

    if new_root != root:
        new_root = _normalize(client, new_root)
    return new_root


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

    def union(self, other_root, merge_func=lambda a, b: b):
        

    def __union(self, root_a, root_b):
        


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
