from .kv import KV


class NameStore:
    def __init__(self, ipfs_api, state_hash):
        self.__ipfs_api = ipfs_api
        self.__names = KV(ipfs_api=ipfs_api, state_hash=state_hash)

    @property
    def state_hash(self):
        return self.__names.state_hash

    def store(self, name, timestamp, resolution):
        name = name.encode('utf8')

        # name -> object relationship
        name_desc = self.__names.get(name)
        kv = KV(ipfs_api=self.__ipfs_api, state_hash=name_desc)
        kv.set(timestamp, resolution.encode('utf8'))
        self.__names.set(name, kv.state_hash)

        # object -> name relationship
        obj_desc = self.__objects.get(resolution.encode('utf8'))
        kv = KV(ipfs_api=self.__ipfs_api, state_hash=obj_desc)
        kv.set(timestamp, name)
        self.__objects.set()
