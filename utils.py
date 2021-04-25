import json
import os

FILE_PATH = os.path.dirname(__file__)

class config:
    def __init__(self, filename, encoding='utf8'):
        self.filename = os.path.join(FILE_PATH, filename)
        self.encoding=encoding
        self.load()
    
    def load(self):
        try:
            with open(self.filename, 'r', encoding=self.encoding) as fp:
                self.json = json.loads(fp.read())
        except FileNotFoundError:
            self.json = {}

    def save(self):
        with open(self.filename, 'w', encoding=self.encoding) as fp:
            fp.write(json.dumps(self.json, indent=True, ensure_ascii=False))

