from flask import Flask, jsonify, request
from flask_restless import APIManager

from models import Name, Object
from db_connection import session

app = Flask(__name__)

api_manager = APIManager(app, session=session)

api_manager.create_api(Name, methods=['GET'])
api_manager.create_api(Object, methods=['GET'])

@app.route('/api/object_search', methods=['GET'])
def object_search():
    query = request.args.get('q')
    objs = Object.full_text_search(session, query).limit(20).all()
    return jsonify(
        [
            {
                'hash': o.hash,
                'properties': {p.name: p.value for p in o.properties},
                'referenced_from': [{
                    'type': r.type,
                    'parent': r.parent_object_hash,
                    'label': r.name,
                } for r in o.parents],
            }
            for o in objs
        ]
    )

if __name__ == '__main__':
    app.run(debug=True)
