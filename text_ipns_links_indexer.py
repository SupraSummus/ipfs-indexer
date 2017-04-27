from links_indexer import RegexpLinksIndexer, NameLinksIndexerMixin


class TextIPNSLinksIndexer(RegexpLinksIndexer, NameLinksIndexerMixin):

    head_size = 128 * 1024
    max_links = 128
    base_property_name = 'text_ipns_links_indexed'
    property_name = '{} {} {}'.format(base_property_name, head_size, max_links)
    link_regexp = 'ipns/([\w\.\-]+)'


if __name__ == '__main__':
    TextIPNSLinksIndexer().loop()
