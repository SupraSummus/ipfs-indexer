import tempfile
import subprocess

from indexer import ContentIndexer

class FileTypeIndexer(ContentIndexer):

    base_property_name = 'file_detected_type'
    head_size = 4 * 1024
    property_name = '{} {}'.format(base_property_name, head_size)

    def get_property_value_for_content(self, hash, data):
        if data is None:
            return None

        with tempfile.NamedTemporaryFile() as fp:
            fp.write(data)
            fp.flush()
            result = subprocess.check_output(['file', '-b', fp.name])
            return result.decode('UTF-8').strip()

if __name__ == '__main__':
    FileTypeIndexer().loop()
