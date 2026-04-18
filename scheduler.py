from typing import List, Dict, Any
from datetime import datetime


def time_to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def has_conflict(course_a: Dict[str, Any], course_b: Dict[str, Any]) -> bool:
    for slot_a in course_a.get("time_slots", []):
        for slot_b in course_b.get("time_slots", []):
            if slot_a["day"] != slot_b["day"]:
                continue

            a_start = time_to_minutes(slot_a["start_time"])
            a_end = time_to_minutes(slot_a["end_time"])
            b_start = time_to_minutes(slot_b["start_time"])
            b_end = time_to_minutes(slot_b["end_time"])

            if max(a_start, b_start) < min(a_end, b_end):
                return True
    return False


def can_add_course(selected: List[Dict[str, Any]], course: Dict[str, Any]) -> bool:
    return all(not has_conflict(existing, course) for existing in selected)


def total_credits(courses: List[Dict[str, Any]]) -> int:
    return sum(course.get("credits", 0) for course in courses)


def max_consecutive_hours(courses: List[Dict[str, Any]]) -> float:
    day_slots: Dict[str, List[tuple]] = {}

    for course in courses:
        for slot in course.get("time_slots", []):
            day = slot["day"]
            start = time_to_minutes(slot["start_time"])
            end = time_to_minutes(slot["end_time"])
            day_slots.setdefault(day, []).append((start, end))

    max_block = 0
    for day, slots in day_slots.items():
        slots.sort()
        current_start, current_end = slots[0]

        for start, end in slots[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
            else:
                max_block = max(max_block, current_end - current_start)
                current_start, current_end = start, end

        max_block = max(max_block, current_end - current_start)

    return round(max_block / 60, 1) if day_slots else 0.0


def build_time_table(courses: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    table: Dict[str, List[Dict[str, Any]]] = {}

    for course in courses:
        for slot in course.get("time_slots", []):
            day = slot["day"]
            table.setdefault(day, []).append({
                "course_code": course["code"],
                "course_name": course["name"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"]
            })

    for day in table:
        table[day].sort(key=lambda x: x["start_time"])

    return table


def analyze_schedule(courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    conflicts = []
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            if has_conflict(courses[i], courses[j]):
                conflicts.append(f'{courses[i]["code"]} and {courses[j]["code"]} time conflict')

    consecutive = max_consecutive_hours(courses)
    score = 100.0

    if conflicts:
        score -= 40
    if consecutive > 3:
        score -= 20
    elif consecutive > 2:
        score -= 10

    advantages = []
    disadvantages = []

    if not conflicts:
        advantages.append("No time conflicts")
    else:
        disadvantages.extend(conflicts)

    if consecutive <= 3:
        advantages.append("Consecutive class time acceptable")
    else:
        disadvantages.append("Consecutive class time is long")

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflict_details": conflicts,
        "consecutive_classes": int(consecutive),
        "max_gap_hours": 0.0,
        "schedule_health_score": max(0.0, score),
        "advantages": advantages,
        "disadvantages": disadvantages
    }


def generate_safe_schedule(courses: List[Dict[str, Any]], max_credits: int = 18) -> Dict[str, Any]:
    sorted_courses = sorted(
        courses,
        key=lambda c: (
            c.get("current_enrollment", 0) / max(c.get("capacity", 1), 1),
            c.get("difficulty", 3.0)
        )
    )

    selected = []
    for course in sorted_courses:
        if total_credits(selected) + course.get("credits", 0) > max_credits:
            continue
        if can_add_course(selected, course):
            selected.append(course)

    return {
        "schedule_type": "safe",
        "selected_courses": selected,
        "total_credits": total_credits(selected),
        "analysis": analyze_schedule(selected),
        "time_table": build_time_table(selected)
    }


def generate_interest_schedule(courses: List[Dict[str, Any]], max_credits: int = 18) -> Dict[str, Any]:
    sorted_courses = sorted(
        courses,
        key=lambda c: (
            c.get("major_requirement", False),
            c.get("core_requirement", False),
            -c.get("difficulty", 3.0)
        ),
        reverse=True
    )

    selected = []
    for course in sorted_courses:
        if total_credits(selected) + course.get("credits", 0) > max_credits:
            continue
        if can_add_course(selected, course):
            selected.append(course)

    return {
        "schedule_type": "interest",
        "selected_courses": selected,
        "total_credits": total_credits(selected),
        "analysis": analyze_schedule(selected),
        "time_table": build_time_table(selected)
    }


def generate_balanced_schedule(courses: List[Dict[str, Any]], max_credits: int = 18) -> Dict[str, Any]:
    sorted_courses = sorted(
        courses,
        key=lambda c: (
            (1 if c.get("major_requirement", False) else 0) +
            (1 if c.get("core_requirement", False) else 0) -
            (c.get("current_enrollment", 0) / max(c.get("capacity", 1), 1)) -
            (c.get("difficulty", 3.0) / 10)
        ),
        reverse=True
    )

    selected = []
    for course in sorted_courses:
        if total_credits(selected) + course.get("credits", 0) > max_credits:
            continue
        if can_add_course(selected, course):
            selected.append(course)

    return {
        "schedule_type": "balanced",
        "selected_courses": selected,
        "total_credits": total_credits(selected),
        "analysis": analyze_schedule(selected),
        "time_table": build_time_table(selected)
    }


def generate_all_schedules(courses: List[Dict[str, Any]], max_credits: int = 18) -> Dict[str, Any]:
    return {
        "schedules": [
            generate_safe_schedule(courses, max_credits),
            generate_interest_schedule(courses, max_credits),
            generate_balanced_schedule(courses, max_credits)
        ],
        "generated_at": datetime.now().isoformat()
    }