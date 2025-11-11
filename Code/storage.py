# storage.py
# JSON storage helpers (safe read/write)

import json
import os
from typing import Any, Dict

DATA_FILE = "data.json"


def load_data() -> Dict[str, Any]:
    """Load DB or return empty structure on missing/corrupt file."""
    if not os.path.exists(DATA_FILE):
        return {"faculties": {}, "students": {}, "classes": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If file is corrupt or unreadable, return clean structure
        return {"faculties": {}, "students": {}, "classes": {}}


def save_data(data: Dict[str, Any]) -> None:
    """Write DB to disk; catch exceptions so UI won't crash."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Warning: failed to save data.json:", e)
