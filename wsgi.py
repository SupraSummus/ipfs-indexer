import os.path
import sys

activate_this = os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, os.path.dirname(__file__))

from rest_api import app as application
