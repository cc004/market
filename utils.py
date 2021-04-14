import json
import os

FILE_PATH = os.path.dirname(__file__)

class config:
    def __init__(self, filename):
        self.filename = os.path.join(FILE_PATH, filename)
        self.load()
    
    def load(self):
        try:
            with open(self.filename, 'r') as fp:
                self.json = json.loads(fp.read())
        except:
            self.json = {}

    def save(self):
        with open(self.filename, 'w') as fp:
            fp.write(json.dumps(self.json, indent=True, ensure_ascii=False))

