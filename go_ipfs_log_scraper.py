import requests
import json
from functools import lru_cache

from models import Name, Object
from db_connection import session

LOG_URL = 'http://localhost:5001/api/v0/log/tail'

def handle_from_dict(key_name):
    def handle(handlers_dict):
        def f(data):
            e = data[key_name]
            return handlers_dict.get(
                e,
                lambda d: print('unknown {}: {}'.format(key_name, e))
            )(data)
        return f
    return handle

handle_events = handle_from_dict('event')
handle_systems = handle_from_dict('system')

def NOOP(data):
    pass

@lru_cache(maxsize=1024)
def store_name(hash):
    if hash.isalnum():
        session.merge(Name(hash=hash))
        session.commit()
        print('name   {}'.format(hash))
    else:
        print('invalid name')

@lru_cache(maxsize=1024)
def store_object(hash):
    #session.merge(Object(hash=hash))
    #session.commit()
    print('object {}'.format(hash))

def key(key, func):
    def f(data):
        return func(data[key])
    return f

def key_if_present(key, func):
    def f(data):
        if key in data:
            func(data[key])
    return f

def many(handlers):
    def f(data):
        return [h(data) for h in handlers]
    return f

"""
handle_systems({
    'dht': handle_events({
        'updatePeer': key('peerID', store_name),
        'handleFindPeerBegin': key('peerID', store_name),
        'handleFindPeer': key('peerID', store_name),
        'handleAddProviderBegin': key('peer', store_name),
        'handleAddProvider': many([key('peer', store_name), key('key', store_object)]),
        'dhtReceivedMessage': print,
        'dhtSentMessage': print,
        'findPeerSingle': key('peerID', store_name),
        'findPeerSingleBegin': key('peerID', store_name),
        'handleGetProvidersBegin': key('peer', store_name),
        'handleGetProviders': many([key('peer', store_name), key('key', store_object)]),
        'FindPeer': key('peerID', store_name),
        'dhtRunBootstrap': NOOP,
        'getValueSingle': print,
        'getValueSingleBegin': print
    }),
    'tcp-tpt': NOOP,
}),
"""

handler = many([
    key_if_present('peerID', store_name),
    key_if_present('peer', store_name),
])

for line in requests.get(LOG_URL, stream=True).iter_lines():
    handler(json.loads(line))
