import datetime
#from sqlalchemy.sql.functions import count, random, 
from sqlalchemy import func
import requests

from models import session, Object, Property, Availability
import settings


def get_object(
    property_name,
    session=session,
    not_available_cooldown_time=datetime.timedelta(days=1),
    base_query=None
):
    """Get object that is doesn't have property and is available."""

    if base_query is None:
        base_query = session.query(Object)

    not_available = session.query(Availability.object_hash)\
        .filter(Availability.available == False)\
        .filter(Availability.time > datetime.datetime.utcnow() - not_available_cooldown_time)

    already_indexed = session.query(Property.object_hash)\
        .filter(Property.name == property_name)

    candidates = base_query\
        .filter(~Object.hash.in_(already_indexed))\
        .filter(~Object.hash.in_(not_available))

    #return candidates.first()
    return candidates.order_by(func.random()).first()
    #return candidates.offset(func.floor(func.random() * func.count(candidates))).first()


def process_object_content(
    hash, func,
    head_size=None,
    session=session,
    cat_api_url=settings.CAT_API_URL
):
    try:
        r = requests.get(
            cat_api_url,
            params={'arg': hash},
            stream=(head_size is not None),
            timeout=10
        )
        if head_size is None:
            data = r.content
        else:
            data = r.raw.read(head_size)
            r.raw.close()
        r.raise_for_status()

        func(session, hash, data)

        session.merge(Availability(object_hash=hash, available=True))

    except requests.exceptions.Timeout:
        print('{} cat timed out'.format(hash))
        session.merge(Availability(object_hash=hash, available=False))

    except requests.HTTPError:
        # cat failed - it may be directory
        func(session, hash, None)

    finally:
        session.commit()

def set_property_based_on_content(hash, property_name, func, **kwargs):
    def f(session, hash, data):
        value = func(hash, data)
        print('{} {}: {}'.format(hash, property_name, value))
        session.merge(Property(object_hash=hash, name=property_name, value=value))
    process_object_content(hash, f, **kwargs)
