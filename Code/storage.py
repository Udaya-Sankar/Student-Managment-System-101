# storage.py
import json
import os
from typing import Dict, Any

DATA_FILE = "data.json"


def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        # initial structure
        return {"faculties": {}, "students": {}, "classes": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
