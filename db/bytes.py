from io import BytesIO

from .ipfs import IPFSBacked


class Bytes(IPFSBacked):
    @classmethod
    def zero_state_hash(self, backend):
        return backend.object_new()['Hash']

    @property
    def value(self):
        v = self.backend.object_data(self.state_hash)
        if len(v) == 0:
            return b''  # for some reason empty data is returned as list
        else:
            return v

    def set(self, value):
        return self.make(
            Bytes,
            self.backend.object_patch_set_data(self.state_hash, BytesIO(value))['Hash'],
        )

    @property
    def valid(self):
        return True  # TODO check if theres no links
