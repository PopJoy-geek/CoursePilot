import json
import os
import csv
from datetime import datetime
from typing import List, Dict, Any

DATA_FILE = "app/sample_data.json"
EXPORT_DIR = "exports"

os.makedirs(EXPORT_DIR, exist_ok=True)


def load_data() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "historical_seat_data": [],
        "monitor_history": []
    }


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def start_monitor(student_id: str, course_codes: List[str]) -> Dict[str, Any]:
    data = load_data()

    monitor_id = f"monitor_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    now = datetime.now().isoformat()

    matched_records = [
        item for item in data.get("historical_seat_data", [])
        if item.get("course_code") in course_codes
    ]

    history_item = {
        "monitor_id": monitor_id,
        "student_id": student_id,
        "start_time": now,
        "end_time": None,
        "duration_minutes": 0,
        "courses_monitored": course_codes,
        "total_checks": len(matched_records),
        "records": matched_records
    }

    if "monitor_history" not in data:
        data["monitor_history"] = []

    data["monitor_history"].append(history_item)
    save_data(data)

    return history_item


def get_monitor_history() -> List[Dict[str, Any]]:
    data = load_data()
    return data.get("monitor_history", [])


def export_monitor_history_csv() -> str:
    data = load_data()
    history = data.get("monitor_history", [])

    filename = f"monitor_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "monitor_id",
            "student_id",
            "course_code",
            "timestamp",
            "current_enrollment"
        ])

        for item in history:
            for record in item.get("records", []):
                writer.writerow([
                    item.get("monitor_id"),
                    item.get("student_id"),
                    record.get("course_code"),
                    record.get("timestamp"),
                    record.get("current_enrollment")
                ])

    return filepath