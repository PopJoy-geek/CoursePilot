from typing import List, Dict, Any


class PrerequisiteChecker:
    """基于输入数据的先修/共修检查器"""

    @staticmethod
    def check_prerequisites(
        completed_courses: List[str],
        course: Dict[str, Any]
    ) -> Dict[str, Any]:
        prerequisites = course.get("prerequisites", []) or []
        corequisites = course.get("corequisites", []) or []

        missing_prereqs = [c for c in prerequisites if c not in completed_courses]
        missing_coreqs = [c for c in corequisites if c not in completed_courses]

        return {
            "course_code": course.get("code"),
            "course_name": course.get("name"),
            "prerequisites_met": len(missing_prereqs) == 0,
            "corequisites_met": len(missing_coreqs) == 0,
            "missing_prerequisites": missing_prereqs,
            "missing_corequisites": missing_coreqs,
            "can_enroll": len(missing_prereqs) == 0,
            "is_key_prerequisite_chain": len(prerequisites) > 0
        }

    @staticmethod
    def batch_check(
        completed_courses: List[str],
        courses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [
            PrerequisiteChecker.check_prerequisites(completed_courses, course)
            for course in courses
        ]