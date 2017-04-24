import datetime
import requests
import time
from sqlalchemy import func

from models import session, Name, Resolution, Object

RESOLVE_URL = 'http://localhost:5001/api/v0/name/resolve'
RESOLUTION_INTERVAL = datetime.timedelta(hours=12)

def get_name_to_resolve():
    already_resolved = session.query(Resolution.name_hash)\
        .filter(Resolution.time > datetime.datetime.utcnow() - RESOLUTION_INTERVAL)
    return session.query(Name)\
        .filter(~Name.hash.in_(already_resolved))\
        .order_by(func.random())\
        .first()

def resolve_name(name):
    resolution_data = requests.get(RESOLVE_URL, params={'arg': name.hash, 'recursive': True}).json()
    resolved_hash = resolution_data.get('Path')
    if resolved_hash is not None:
        resolved_hash = resolved_hash.replace('/ipfs/', '')
        session.merge(Object(hash=resolved_hash))

    session.merge(Resolution(name_hash=name.hash, object_hash=resolved_hash))

    session.commit()

    return resolved_hash

while True:
    name = get_name_to_resolve()
    if name:
        print('resolving {}'.format(name.hash))
        resolved = resolve_name(name)
        print('resolved  {} to {}'.format(name.hash, resolved))
    else:
        print('nothing to do')
        time.sleep(60)
