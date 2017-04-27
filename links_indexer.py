import re

from indexer import Indexer, ContentIndexerMixin
from file_type_indexer import FileTypeIndexer
from models import Link, NameReference, Property, Object, Name


class LinksIndexer(Indexer):
    """Saves links when processing objects.

    Subclasses must set class variables:
     * max_links - link limit in single object (None for no limit)
     * link_type
    """

    def get_links(self, hash):
        raise NotImplementedError()

    def save_link(self, hash, label, target):
        raise NotImplementedError()

    def get_property_value_for_object(self, hash):
        return None # just to mark that it's been processed

    def process_object(self, hash):
        links = self.get_links(hash)
        if self.max_links is not None:
            links = links[:self.max_links]

        for target, label in links:
            self.save_link(hash, label, target)

        print('{} {} links: {}'.format(hash, self.link_type, len(links)))

        super().process_object(hash)


class ContentLinksIndexer(LinksIndexer, ContentIndexerMixin):

    def get_links_from_content(self, hash, data):
        raise NotImplementedError()

    def get_links(self, hash):
        data = self.get_content(hash)
        return self.get_links_from_content(hash, data)


class ObjectLinksIndexerMixin(LinksIndexer):

    def save_link(self, hash, label, target):
        self.session.merge(Object(
            hash=target
        ))
        self.session.merge(Link(
            parent_object_hash=hash,
            child_object_hash=target,
            type=self.link_type,
            name=label
        ))


class NameLinksIndexerMixin(LinksIndexer):

    def save_link(self, hash, label, target):
        self.session.merge(Name(
            hash=target
        ))
        self.session.merge(NameReference(
            object_hash=hash,
            name_hash=target,
            type=self.link_type,
            label=label
        ))


class RegexpLinksIndexer(ContentLinksIndexer):
    """Extracts links from plain text using regex.

    Subclasses must set class variables:
     * link_regexp - regex to match the links. It should have () group
       that returns link target.
    """

    link_type = 'text'

    @property
    def base_query(self):
        text_hashes = self.session.query(Property.object_hash)\
            .filter(Property.name.ilike(FileTypeIndexer.base_property_name + '%'))\
            .filter(Property.value.ilike('%text%'))
        return self.session.query(Object)\
            .filter(Object.hash.in_(text_hashes))

    def get_links_from_content(self, hash, data):
        if data is None:
            return []
        ms = re.findall(self.link_regexp, data.decode('ASCII', 'replace'))
        return [(match, '') for match in ms]
