from flask import Flask, jsonify, request
from flask_restless import APIManager
from math import ceil

from models import Name, Object
from db_connection import session
import settings

app = Flask(__name__)

api_manager = APIManager(app, session=session)

api_manager.create_api(Name, methods=['GET'])
api_manager.create_api(Object, methods=['GET'])

@app.route('/api/object_search', methods=['GET'])
def object_search():
    query = request.args.get('q', '')
    page = max(0, int(request.args.get('page', '0')))
    page_size = 20
    objs = Object.full_text_search(session, query)
    num_objs = objs.count()
    return jsonify({
        'page': page,
        'num_results': num_objs,
        'num_pages': ceil(num_objs/page_size),
        'objects': [
            {
                'hash': o.hash,
                'properties': {p.name: p.value for p in o.properties},
                'referenced_from': [{
                    'type': r.type,
                    'parent': r.parent_object_hash,
                    'label': r.name,
                } for r in o.parents],
            } for o in objs.offset(page_size * page).limit(page_size)
        ],
    })

if __name__ == '__main__':
    app.run(
        debug=settings.FLASK_DEBUG,
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT
    )
