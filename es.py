from elasticsearch import Elasticsearch
import datetime
import logging

logger = logging.getLogger(__name__)
es = Elasticsearch()

index = 'ipfs_index'

def name(name):
    es.update(index=index, doc_type='name', id=name, body={
        'doc': {},
        'upsert': {'resolutions': [], 'referenced_from': []},
    })
    logger.info('name {}'.format(name))

def name_resolved(name, hash): # deosnt work ;/
    es.update(index=index, doc_type='name', id=name, body={
        'script': {
            'lang': 'painless',
            'inline': 'ctx._source.resolutions += params.resolution',
            'params': {'resolution': {
                'hash': hash,
                'date': datetime.datetime.utcnow()
            }},
        },
    })
    logger.info('name {} resolved to {}'.format(name, hash))
