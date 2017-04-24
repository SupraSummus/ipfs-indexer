import time
import re

from models import session, Link, Object, Property
from utils import get_object, process_object_content
import settings
import file_tagger

HEAD_SIZE = 128 * 1024
MAX_LINKS = 128
BASE_PROPERTY_NAME = 'text_ipfs_links_indexed'
PROPERTY_NAME = '{} {} {}'.format(BASE_PROPERTY_NAME, HEAD_SIZE, MAX_LINKS)
LINK_TYPE = 'text'

def index_text_ipfs_links(session, hash, data):
    if data is None:
        return None

    ms = re.findall('ipfs/([a-zA-Z0-9]+)', data.decode('ASCII', 'replace'))
    for match in ms[:MAX_LINKS]:
        session.merge(Object(hash=match))
        session.merge(Link(parent_object_hash=hash, child_object_hash=match, type=LINK_TYPE, name=''))
    session.merge(Property(object_hash=hash, name=PROPERTY_NAME, value=None))

def loop(session=session, sleep_seconds=60, cat_api_url=settings.CAT_API_URL):
    while True:
        html_hashes = session.query(Property.object_hash)\
            .filter(Property.name.ilike(file_tagger.BASE_PROPERTY_NAME + '%'))\
            .filter(Property.value.ilike('%text%'))
        base_query = session.query(Object)\
            .filter(Object.hash.in_(html_hashes))
        obj = get_object(PROPERTY_NAME, base_query=base_query, session=session)
        if obj:
            print('indexing text IPFS links in {}'.format(obj.hash))
            process_object_content(obj.hash, index_text_ipfs_links, head_size=HEAD_SIZE, session=session, cat_api_url=cat_api_url)
        else:
            print('nothing to do')
            time.sleep(sleep_seconds)

if __name__ == '__main__':
    loop()
