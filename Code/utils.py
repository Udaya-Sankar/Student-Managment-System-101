# utils.py
import random
import string
import csv
from typing import Dict, Any, List, Tuple


def generate_student_id(roll_no: str) -> str:
    """Roll-number-based unique student id."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"STU_{roll_no}_{suffix}"


def generate_temp_password(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def compute_totals_and_ranks(data: Dict[str, Any], class_id: str) -> Dict[str, Dict[str, int]]:
    """
    Return { student_id: {"total": int, "rank": int} } for students in the class.
    """
    cls = data["classes"].get(class_id)
    if not cls:
        return {}
    subjects: List[str] = cls.get("subjects", [])
    totals: List[Tuple[str, int]] = []
    for sid in cls.get("students", []):
        student = data["students"].get(sid, {})
        total = 0
        for sub in subjects:
            try:
                total += int(student.get("marks", {}).get(sub, 0))
            except Exception:
                total += 0
        totals.append((sid, total))
    totals.sort(key=lambda x: (-x[1], x[0]))
    ranks: Dict[str, Dict[str, int]] = {}
    prev_total = None
    prev_rank = 0
    for i, (sid, total) in enumerate(totals, start=1):
        if total != prev_total:
            rank = i
            prev_rank = rank
            prev_total = total
        else:
            rank = prev_rank
        ranks[sid] = {"total": total, "rank": rank}
    return ranks


def export_rank_list_csv(data: Dict[str, Any], class_id: str, filename: str) -> None:
    """
    Export rank list (student id, name, total, rank, marks...) to CSV.
    """
    cls = data["classes"].get(class_id)
    if not cls:
        raise ValueError("Class not found")
    subjects = cls.get("subjects", [])
    ranks = compute_totals_and_ranks(data, class_id)
    # prepare header
    header = ["rank", "student_id", "student_name", "total"] + subjects
    rows: List[List] = []
    # sort by rank
    arr = sorted([(info["rank"], sid, info["total"]) for sid, info in ranks.items()], key=lambda x: x[0])
    for rank, sid, total in arr:
        student = data["students"].get(sid, {})
        row = [rank, sid, student.get("name", ""), total]
        for sub in subjects:
            row.append(student.get("marks", {}).get(sub, 0))
        rows.append(row)
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
