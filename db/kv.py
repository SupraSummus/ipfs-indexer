import urllib.parse
from functools import lru_cache
import logging

from .ipfs import IPFSBacked


logger = logging.getLogger(__name__)


def KV(value_type):
    class __KV(IPFSBacked):
        """Map object that holds mapping bytestring -> ipfs object.
        Implemented as radix tree... OMG! It's a trie!
        """
        __CHILD_LINK_PREFIX = 'c'
        __LEAF_LINK_PREFIX = 'd'
        __MAX_KEY_LENGTH = 64  # TODO this is currently ignored

        @classmethod
        def zero_state_hash(cls, backend):
            return backend.object_new()['Hash']

        def set(self, key, value):
            assert isinstance(key, bytes)
            assert isinstance(value, value_type)

            # find prefix existing already in the tree
            common_prefix_length, child_key, is_leaf, child_hash = self.__find_common_prefix(key)

            # (no common prefix found) or (there is leaf with exact same key) - insert key as a leaf
            if (
                (common_prefix_length == 0) or
                (is_leaf and child_key == key)
            ):
                if value.is_zero:
                    return self.__remove_link(True, key).__squashed
                else:
                    return self.__set_link(True, key, value.state_hash)

            elif is_leaf:
                if value.is_zero:
                    return self
                else:
                    return self.__remove_link(True, child_key).__set_link(
                        False,
                        key[:common_prefix_length],
                        self.make_self().__set_link(
                            True,
                            child_key[common_prefix_length:],
                            child_hash,
                        ).__set_link(
                            True,
                            key[common_prefix_length:],
                            value.state_hash,
                        ).state_hash,
                    )

            else:
                if common_prefix_length < len(child_key):
                    # part of the key is shared - create a new subtree and add old values and new one to it
                    child = self.make_self().__set_link(
                        False,
                        child_key[common_prefix_length:],
                        child_hash,
                    )

                else:  # common_prefix_length == len(child_key)
                    # just delegate adding to subtree
                    child = self.make_self(child_hash)

                updated_child = child.set(key[common_prefix_length:], value)
                if updated_child.is_zero:
                    return self.__remove_link(False, child_key).__squashed
                elif child == updated_child:
                    return self
                else:
                    new = self
                    if child_key != child_key[:common_prefix_length]:
                        new = self.__remove_link(False, child_key)
                    return new.__set_link(
                        False,
                        child_key[:common_prefix_length],
                        updated_child.state_hash,
                    ).__squashed

        def get(self, key):
            assert isinstance(key, bytes)
            entries = list(self.entries(gte=key, lt=key + b'\0'))
            if len(entries) == 0:
                return self.make(value_type)
            else:
                return entries[0][1]

        def entries(self, gte=b'', lt=None, reverse=False, key_length_limit=None):
            for key, is_leaf, state_hash in sorted(self.__links, reverse=reverse):
                if is_leaf:
                    if (
                        key >= gte and
                        (lt is None or key < lt) and
                        (key_length_limit is None or len(key) <= key_length_limit)
                    ):
                        yield key, self.make(value_type, state_hash)

                else:
                    if (
                        key >= gte[:len(key)] and
                        (lt is None or key < lt) and
                        (key_length_limit is None or len(key) <= key_length_limit)
                    ):
                        for k, v in self.make_self(state_hash).entries(
                            gte[len(key):],
                            None if lt is None else lt[len(key):],
                            reverse,
                            None if key_length_limit is None else key_length_limit - len(key),
                        ):
                            yield key + k, v

        @property
        def dump(self):
            d = {}
            for key, is_leaf, state_hash in self.__links:
                if is_leaf:
                    d[key] = state_hash
                else:
                    d[key] = self.make_self(state_hash).dump
            return d

        def __set_link(self, is_leaf, key, state_hash):
            return self.make_self(self.backend.object_patch_add_link(
                self.state_hash,
                self.__link_name(is_leaf, key),
                state_hash,
            )['Hash'])

        def __remove_link(self, is_leaf, key):
            return self.make_self(self.backend.object_patch_rm_link(
                self.state_hash,
                self.__link_name(is_leaf, key),
            )['Hash'])

        def __link_name(self, is_leaf, key):
            return {
                True: self.__LEAF_LINK_PREFIX,
                False: self.__CHILD_LINK_PREFIX,
            }[is_leaf] + self.__escape_key(key),

        @property
        @lru_cache(maxsize=1024)
        def __links(self):
            links = []
            for link in self.backend.object_links(self.state_hash).get('Links', []):
                name = link['Name']
                if name.startswith(self.__LEAF_LINK_PREFIX):
                    is_leaf = True
                    name = name[len(self.__LEAF_LINK_PREFIX):]
                elif name.startswith(self.__CHILD_LINK_PREFIX):
                    is_leaf = False
                    name = name[len(self.__CHILD_LINK_PREFIX):]
                else:
                    logger.warning("KV %s: couldnt determine type for link '%s'", self.state_hash, name)
                    continue
                links.append((self.__unescape_key(name), is_leaf, link['Hash']))
            return links

        @staticmethod
        def __escape_key(key):
            return urllib.parse.quote_from_bytes(key, safe=' ')

        @staticmethod
        def __unescape_key(key):
            return urllib.parse.unquote_to_bytes(key)

        def __find_common_prefix(self, key):
            for child_key, is_leaf, child_hash in self.__links:
                # they are the same
                if child_key == key:
                    return len(key), key, is_leaf, child_hash

                # find common prefix length
                max_common_prefix_length = min(len(child_key), len(key))
                common_prefix_length = 0
                while (
                    common_prefix_length < max_common_prefix_length and
                    child_key[common_prefix_length] == key[common_prefix_length]
                ):
                    common_prefix_length += 1

                # if there's even smallest common prefix then we cant do better
                # (because we are searching keys of radix tree)
                if common_prefix_length > 0:
                    return common_prefix_length, child_key, is_leaf, child_hash

            return 0, None, None, None

        @property
        def __squashed(self):
            """Squash single layer of the tree if possible.
            (It is possible when there is only one child link.)
            """
            if len(self.__links) == 1 and not self.__links[0][1]:  # single child link
                key_prefix = self.__links[0][0]
                child_hash = self.__links[0][2]
                new = self.make_self()
                for key, is_leaf, state_hash in self.make_self(child_hash).__links:
                    new = new.__set_link(is_leaf, key_prefix + key, state_hash)
                return new
            else:
                return self

    return __KV
