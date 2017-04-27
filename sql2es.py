from sqlalchemy import func
from sqlalchemy.orm import joinedload
from pprint import pprint

from models import session, Object, Name
from es import es, index


def store_object(obj):
    flat = {
        'properties': {prop.name: (prop.value or True) for prop in obj.properties},
        'availability': [{'date': a.time, 'available': a.available} for a in obj.availability],
        'referenced_from': [{'hash': r.parent_object_hash, 'type': r.type, 'name': r.name} for r in obj.parents],
    }
    es.index(index=index, doc_type='object', id=obj.hash, body=flat)
    print('object', obj.hash)

def store_name(name):
    flat = {
        'resolutions': [{'date': r.time, 'hash': r.object_hash} for r in name.resolutions]
    }
    es.index(index=index, doc_type='name', id=name.hash, body=flat)
    print('name', name.hash)

for obj in session.query(Object).options(
    joinedload(Object.properties),
    joinedload(Object.availability),
    joinedload(Object.parents)
).all():
    store_object(obj)

for name in session.query(Name).options(
    joinedload(Name.resolutions)
).all():
    store_name(name)
