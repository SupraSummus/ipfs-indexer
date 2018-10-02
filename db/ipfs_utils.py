from io import BytesIO
import urllib.parse
from functools import lru_cache


def escape_link_name(name):
    return urllib.parse.quote(name, safe='')


def unescape_link_name(escaped):
    return urllib.parse.unquote(escaped)


def object_new(backend, data, links):
    root = backend.object_new()['Hash']
    root = backend.object_patch_set_data(root, BytesIO(data))['Hash']
    for link_name, target in links.items():
        root = object_set_link(backend, root, link_name, target)
    return root


@lru_cache(maxsize=1024)
def object_links(backend, root):
    return {
        unescape_link_name(link['Name']): link['Hash']
        for link in backend.object_links(root).get('Links', [])
    }


def object_get_link(backend, root, link_name):
    return object_links(backend, root)[link_name]


def object_set_link(backend, root, link_name, target):
    return backend.object_patch_add_link(root, escape_link_name(link_name), target)['Hash']
