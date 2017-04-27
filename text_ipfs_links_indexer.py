from links_indexer import RegexpLinksIndexer, ObjectLinksIndexerMixin


class TextIPFSLinksIndexer(RegexpLinksIndexer, ObjectLinksIndexerMixin):

    head_size = 128 * 1024
    max_links = 128
    base_property_name = 'text_ipfs_links_indexed'
    property_name = '{} {} {}'.format(base_property_name, head_size, max_links)
    link_regexp = 'ipfs/([a-zA-Z0-9]+)'


if __name__ == '__main__':
    TextIPFSLinksIndexer().loop()
