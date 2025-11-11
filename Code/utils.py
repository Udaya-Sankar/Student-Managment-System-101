# utils.py
# Helpers for ID/password generation and ranking.

import random
import string
from typing import Dict, Any, List, Tuple


def generate_student_id(roll_no: str) -> str:
    """Student ID derived from roll_no plus random suffix."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"STU_{roll_no}_{suffix}"


def generate_temp_password(length: int = 8) -> str:
    """Generate a random alphanumeric password."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def compute_totals_and_ranks(data: Dict[str, Any], class_id: str) -> Dict[str, Dict[str, int]]:
    """
    For the class compute totals and ranks.
    Returns mapping: student_id -> {"total": int, "rank": int}
    Ties share same rank (dense ranking).
    """
    cls = data.get("classes", {}).get(class_id)
    if not cls:
        return {}
    subjects: List[str] = cls.get("subjects", []) or []
    totals: List[Tuple[str, int]] = []
    for sid in cls.get("students", []) or []:
        student = data.get("students", {}).get(sid, {})
        total = 0
        for sub in subjects:
            try:
                total += int(student.get("marks", {}).get(sub, 0))
            except Exception:
                total += 0
        totals.append((sid, total))
    totals.sort(key=lambda x: (-x[1], x[0]))  # highest total first
    ranks: Dict[str, Dict[str, int]] = {}
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
