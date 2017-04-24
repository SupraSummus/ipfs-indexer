import requests
import time
import datetime
import tempfile
import subprocess

from models import session, Property, Availability
from utils import get_object

CAT_API_URL = 'http://localhost:5001/api/v0/cat'
PROPERTY_NAME = 'file_detected_type'
NOT_AVAILABLE_COOLDOWN_TIME = datetime.timedelta(days=1)
HEAD_SIZE = 4 * 1024

def detect_type(obj):
    try:
        r = requests.get(
            CAT_API_URL,
            params={'arg': obj.hash},
            stream=True,
            timeout=10
        )
        head = r.raw.read(HEAD_SIZE)
        r.raw.close()

        if r.status_code == requests.codes.ok:

            with tempfile.NamedTemporaryFile() as fp:
                fp.write(head)
                fp.flush()
                result = subprocess.run(['file', '-b', fp.name], stdout=subprocess.PIPE, encoding='UTF-8')
                print(str(result.stdout).strip())
                session.merge(Property(object_hash=obj.hash, name=PROPERTY_NAME, value=str(result.stdout).strip()))

            session.merge(Availability(object_hash=obj.hash, available=True))
            session.commit()

        else:
            session.merge(Property(object_hash=obj.hash, name=PROPERTY_NAME, value=None))
            session.commit()

    except requests.exceptions.Timeout:
        print('timed-out')
        session.merge(Availability(object_hash=obj.hash, available=False))
        session.commit()

if __name__ == '__main__':
    while True:
        obj = get_object(PROPERTY_NAME)
        if obj:
            print('doing {}'.format(obj.hash))
            detect_type(obj)
        else:
            print('nothing to do')
            time.sleep(60)
