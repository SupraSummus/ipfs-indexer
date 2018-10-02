from .ipfs_utils import object_new, object_get_link, object_set_link, object_links
from .ipfs import IPFSBacked


def Record(fields):
    class __Record(IPFSBacked):
        @classmethod
        def zero_state_hash(self, backend):
            return object_new(backend, b'', {
                k: t.zero_state_hash(backend)
                for k, t in fields.items()
            })

        def get(self, name):
            assert name in fields
            return fields[name](
                self.backend,
                object_get_link(self.backend, self.state_hash, name),
            )

        def set(self, name, value):
            assert name in fields
            assert isinstance(value, fields[name])
            return self.make_self(
                object_set_link(self.backend, self.state_hash, name, value.state_hash),
            )

        @property
        def valid(self):
            links = object_links(self.backend, self.state_hash)
            if links.keys() != fields.keys():
                return False
            for k, state in links:
                if not self.make(fields[k], state).valid:
                    return False
            return True

    return __Record
