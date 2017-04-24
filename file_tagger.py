import time
import tempfile
import subprocess

from models import session
from utils import get_object, set_property_based_on_content
import settings

BASE_PROPERTY_NAME = 'file_detected_type'
HEAD_SIZE = 4 * 1024
PROPERTY_NAME = '{} {}'.format(BASE_PROPERTY_NAME, HEAD_SIZE)

def get_type(hash, data):
    if data is None:
        return None

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(data)
        fp.flush()
        result = subprocess.run(['file', '-b', fp.name], stdout=subprocess.PIPE, encoding='UTF-8')
        return result.stdout.strip()

def loop(session=session, **kwargs):
    while True:
        obj = get_object(PROPERTY_NAME, session=session)
        if obj:
            set_property_based_on_content(
                obj.hash, PROPERTY_NAME, get_type,
                head_size=HEAD_SIZE,
                session=session,
                **kwargs
            )
        else:
            print('nothing to do')
            time.sleep(60)

if __name__ == '__main__':
    loop()
