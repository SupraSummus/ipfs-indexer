import re

from models import Object, Property
from file_type_indexer import FileTypeIndexer
from indexer import ContentLinksIndexer


class TextIPFSLinksIndexer(ContentLinksIndexer):

    head_size = 128 * 1024
    max_links = 128
    base_property_name = 'text_ipfs_links_indexed'
    property_name = '{} {} {}'.format(base_property_name, head_size, max_links)
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
        ms = re.findall('ipfs/([a-zA-Z0-9]+)', data.decode('ASCII', 'replace'))
        return [(match, '') for match in ms]

if __name__ == '__main__':
    TextIPFSLinksIndexer().loop()
