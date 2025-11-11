# storage.py
# Simple JSON persistence for the app.

import json
import os

DATA_FILE = "data.json"


def load_data():
    """
    Return structure:
    {
      "faculties": { username: { "name": ..., "password": ... } },
      "students":  { student_id: { "name": ..., "password": ..., "first_login": bool, "class_id": cid, "marks": {subject: int, ...} } },
      "classes":   { class_id: { "name": ..., "faculty": username, "subjects": [...], "students": [student_id, ...] } }
    }
    """
    if not os.path.exists(DATA_FILE):
        return {"faculties": {}, "students": {}, "classes": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
