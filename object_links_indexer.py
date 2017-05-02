import requests

from models import Availability
from indexer import ObjectNotAvailable
from links_indexer import LinksIndexer, ObjectLinksIndexerMixin
import settings


class ObjectLinksIndexer(ObjectLinksIndexerMixin):
    """Extracts links from IPFS DAG."""

    max_links = None
    property_name = 'dir_links_indexed'
    link_type = 'dir'

    def __init__(self,
        *args,
        object_links_api_url=settings.IPFS_LINKS_API_URL,
        timeout=10,
        **kwargs
    ):
        self.object_links_api_url = object_links_api_url
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def get_links(self, hash):
        try:
            r = requests.get(
                self.object_links_api_url,
                params={'arg': hash},
                timeout=self.timeout
            )
            r.raise_for_status()
            links = r.json().get('Links', [])
            self.session.merge(Availability(object_hash=hash, available=True))
            return [
                (link['Hash'], link['Name'])
                for link in links
                if link['Name'] != ''
            ]

        except (requests.exceptions.Timeout, requests.HTTPError):
            raise ObjectNotAvailable()


if __name__ == '__main__':
    ObjectLinksIndexer().loop()
