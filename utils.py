import datetime
#from sqlalchemy.sql.functions import count, random, 
from sqlalchemy import func

from models import session, Object, Property, Availability


def get_or_create(session, model, args):
    instance = session.query(model).filter_by(**args).first()
    if instance:
        return instance
    else:
        instance = model(**args)
        session.add(instance)
        return instance


def get_object(property_name, not_available_cooldown_time=datetime.timedelta(days=1)):
    """Get object that is doesn't have property and is available."""
    not_available = session.query(Availability.object_hash)\
        .filter(Availability.available == False)\
        .filter(Availability.time > datetime.datetime.utcnow() - not_available_cooldown_time)
    already_indexed = session.query(Property.object_hash)\
        .filter(Property.name == property_name)
    candidates = session.query(Object)\
        .filter(~Object.hash.in_(already_indexed))\
        .filter(~Object.hash.in_(not_available))
    #return candidates.first()
    return candidates.order_by(func.random()).first()
    #return candidates.offset(func.floor(func.random() * func.count(candidates))).first()
