from db_connection import session
from models import Object, Name, Property
from object_links_indexer import ObjectLinksIndexer
from file_type_indexer import FileTypeIndexer
from .models import Measurement


class BaseMonitor():
    def save(self):
        raise NotImplementedError()


class Monitor(BaseMonitor):

    def __init__(self, session=session):
        self.session = session

    def measure(self):
        raise NotImplementedError()

    def save(self):
        self.session.merge(Measurement(
            name=self.name,
            value=self.measure()
        ))
        self.session.commit()


class BulkMonitor(BaseMonitor):

    def __init__(self, monitors):
        self.monitors = monitors

    def save(self):
        for monitor in self.monitors:
            monitor.save()


class QueryCountMonitor(Monitor):

    def __init__(self, name, query, **kwargs):
        self.name = name
        self.query = query
        super().__init__(**kwargs)

    def measure(self):
        return self.query.count()


class ObjectPropertyMonitor(QueryCountMonitor):

    def __init__(self, property_name, read_session=session, **kwargs):
        super().__init__(
            name=property_name,
            query=read_session\
                .query(Property.object_hash)\
                .filter(Property.name==property_name),
            **kwargs
        )


monitor = BulkMonitor([
    QueryCountMonitor(name='all objects', query=session.query(Object)),
    QueryCountMonitor(name='all names', query=session.query(Name)),
    ObjectPropertyMonitor(property_name=ObjectLinksIndexer.property_name),
    ObjectPropertyMonitor(property_name=FileTypeIndexer.property_name),
])
