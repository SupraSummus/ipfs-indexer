class IPFSBacked:
    @classmethod
    def zero_state_hash(cls, backend):
        raise NotImplementedError()

    def __init__(self, backend, state_hash=None):
        if state_hash is None:
            state_hash = self.zero_state_hash(backend)

        self.__backend = backend
        self.__state_hash = state_hash

    @property
    def backend(self):
        return self.__backend

    @property
    def state_hash(self):
        return self.__state_hash

    @property
    def is_zero(self):
        return self.__state_hash == self.zero_state_hash(self.__backend)

    @property
    def valid(self):
        raise NotImplementedError()

    def make(self, another_type, state_hash=None):
        assert issubclass(another_type, IPFSBacked)
        return another_type(backend=self.__backend, state_hash=state_hash)

    def make_self(self, state_hash=None):
        return self.make(self.__class__, state_hash)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__state_hash == other.state_hash

    def __hash__(self):
        return hash((self.__class__, self.__state_hash))

    def __repr__(self):
        return '{}(backend={}, state_hash={})'.format(
            repr(self.__class__),
            repr(self.__backend),
            repr(self.__state_hash),
        )
