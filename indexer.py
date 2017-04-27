import datetime
from sqlalchemy import func
from functools import lru_cache
import requests
import time

from models import session, Object, Availability, Property
import settings


class ObjectNotAvailable(Exception):
    pass


class Indexer:
    """Finds object without property and processes them.

    Subclasses must set class variables:
     * property_name
    """

    def __init__(self,
        *args,
        session=session,
        sleep_seconds=60,
        not_available_cooldown_time=datetime.timedelta(days=1),
        **kwargs
    ):
        self.session = session
        self.sleep_seconds = sleep_seconds
        self.not_available_cooldown_time = not_available_cooldown_time
        super().__init__(*args, **kwargs)

    def get_property_value_for_object(self, hash):
        raise NotImplementedError()

    @property
    def base_query(self):
        return self.session.query(Object)

    def get_object(self):
        """Get object that doesn't have property and is available."""

        not_available = self.session.query(Availability.object_hash)\
            .filter(Availability.available == False)\
            .filter(Availability.time > datetime.datetime.utcnow() - self.not_available_cooldown_time)

        already_indexed = self.session.query(Property.object_hash)\
            .filter(Property.name == self.property_name)

        candidates = self.base_query\
            .filter(~Object.hash.in_(already_indexed))\
            .filter(~Object.hash.in_(not_available))

        #return candidates.first()
        return candidates.order_by(func.random()).first()
        #return candidates.offset(func.floor(func.random() * func.count(candidates))).first()

    def process_object(self, hash):
        property_value = self.get_property_value_for_object(hash)
        self.session.merge(Property(
            object_hash=hash,
            name=self.property_name,
            value=property_value
        ))
        print('{} {}: {}'.format(hash, self.property_name, property_value))

    def loop(self):
        while True:
            obj = self.get_object()
            if obj:
                try:
                    self.process_object(obj.hash)
                except ObjectNotAvailable:
                    print('{} na'.format(obj.hash))
                finally:
                    self.session.commit()
            else:
                print('nothing to do')
                time.sleep(self.sleep_seconds)


class ContentIndexerMixin():
    """Provides method for retriving object content.

    Subclasses must set class variables:
     * head_size - retrive at most this many bytes (None for no limit)
    """

    def __init__(self,
        *args,
        cat_api_url=settings.CAT_API_URL,
        cat_timeout=10,
        **kwargs
    ):
        self.cat_api_url = cat_api_url
        self.cat_timeout = cat_timeout
        super().__init__(*args, **kwargs)

    def get_content(self, hash):
        try:
            r = requests.get(
                self.cat_api_url,
                params={'arg': hash},
                stream=(self.head_size is not None),
                timeout=self.cat_timeout
            )
            if self.head_size is None:
                data = r.content
            else:
                data = r.raw.read(self.head_size)
                r.raw.close()
            r.raise_for_status()

            self.session.merge(Availability(object_hash=hash, available=True))

            return data

        except requests.exceptions.Timeout:
            self.session.merge(Availability(object_hash=hash, available=False))
            raise ObjectNotAvailable()

        except requests.HTTPError:
            # cat failed - it may be directory
            return None


class ContentIndexer(Indexer, ContentIndexerMixin):
    """Sets property based on object content."""

    def get_property_value_for_content(self, hash, data):
        raise NotImplementedError()

    def get_property_value_for_object(self, hash):
        data = self.get_content(hash)
        return self.get_property_value_for_content(hash, data)
