# utils.py
# Helpers: ID/password generation, ranking computation.

import random
import string
from typing import Dict, Tuple


def generate_student_id(roll_no: str) -> str:
    """Produce stable-looking unique id from roll and short random suffix."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"STU_{roll_no}_{suffix}"


def generate_temp_password(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def compute_totals_and_ranks(data: Dict, class_id: str) -> Dict[str, Dict[str, int]]:
    """
    For a given class_id compute total marks and rank for each student in that class.
    Returns dict: { student_id: { "total": int, "rank": int } }
    """
    cls = data["classes"].get(class_id)
    if not cls:
        return {}
    subjects = cls.get("subjects", [])
    totals = []
    for sid in cls.get("students", []):
        student = data["students"].get(sid, {})
        total = 0
        for sub in subjects:
            total += int(student.get("marks", {}).get(sub, 0))
        totals.append((sid, total))
    # sort descending total, then by id to keep deterministic order
    totals.sort(key=lambda x: (-x[1], x[0]))
    ranks = {}
    prev_total = None
    prev_rank = 0
    for idx, (sid, total) in enumerate(totals, start=1):
        if total != prev_total:
            rank = idx
            prev_rank = rank
            prev_total = total
        else:
            rank = prev_rank
        ranks[sid] = {"total": total, "rank": rank}
    return ranks
