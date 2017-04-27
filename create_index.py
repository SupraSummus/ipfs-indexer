from es import es, index

es.indices.create('ipfs_index', ignore=400)

es.indices.put_mapping(
    index=index,
    doc_type='object',
    body={
        'dynamic': 'strict',
        'properties': {

            'properties': {
                'dynamic': True,
                'properties': {},
            },

            'availability': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'available': {'type': 'boolean'},
                    'date': {'type': 'date'},
                },
            },

            'referenced_from': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'type': {'type': 'keyword'},
                    'hash': {'type': 'keyword'},
                    'name': {'type': 'text'},
                },
            },

        },
    }
)

es.indices.put_mapping(
    index=index,
    doc_type='name',
    body={
        'dynamic': 'strict',
        'properties': {

            'referenced_from': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'type': {'type': 'keyword'},
                    'hash': {'type': 'keyword'},
                    'name': {'type': 'text'},
                },
            },

            'resolutions': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'hash': {'type': 'keyword'},
                    'date': {'type': 'date'},
                },
            },

        },
    }
)
