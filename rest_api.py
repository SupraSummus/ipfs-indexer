from flask import Flask
from flask_restless import APIManager

from models import session, Name, Object

app = Flask(__name__)

api_manager = APIManager(app, session=session)

api_manager.create_api(Name, methods=['GET'])
api_manager.create_api(Object, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
