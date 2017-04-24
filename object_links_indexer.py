import requests
import time
import datetime

from models import session, Object, Property, Availability, Link
from utils import get_object

LINKS_API_URL = 'http://localhost:5001/api/v0/object/links'
TAG_OF_INDEXED_OBJECTS = 'dir_links_indexed'
NOT_AVAILABLE_COOLDOWN_TIME = datetime.timedelta(days=1)
TYPE_OF_LINKS = 'dir'

def index_links(obj):
    try:
        r = requests.get(
            LINKS_API_URL,
            params={'arg': obj.hash},
            timeout=10
        )
        r.raise_for_status()
        links = r.json().get('Links', [])

        n = 0
        for link in links:
            if link['Name'] != '':
                session.merge(Object(hash=link['Hash']))
                session.merge(Link(
                    parent_object_hash=obj.hash,
                    child_object_hash=link['Hash'],
                    type=TYPE_OF_LINKS,
                    name=link['Name']
                ))
                n += 1

        session.merge(Property(
            object_hash=obj.hash,
            name=TAG_OF_INDEXED_OBJECTS,
            value=None
        ))
        session.merge(Availability(object_hash=obj.hash, available=True))
        session.commit()
        return n

    except (requests.exceptions.Timeout, requests.HTTPError):
        print('timed-out')
        session.merge(Availability(object_hash=obj.hash, available=False))
        session.commit()
        return 0

while True:
    obj = get_object(TAG_OF_INDEXED_OBJECTS)
    if obj:
        print('indexing links in  \t{}'.format(obj.hash))
        n = index_links(obj)
        print('indexed {} links in \t{}'.format(n, obj.hash))
    else:
        print('nothing to do')
        time.sleep(60)
