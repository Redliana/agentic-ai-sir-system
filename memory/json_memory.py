# memory/json_memory.py

import json
import os

class JSONMemory:
    def __init__(self, filepath="memory/memory.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump({}, f)

    def load(self):
        with open(self.filepath, "r") as f:
            return json.load(f)

    def save(self, key, value):
        data = self.load()
        data[key] = value
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def get(self, key, default=None):
        return self.load().get(key, default)
