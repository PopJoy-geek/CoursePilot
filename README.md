# CoursePilot
AI-powered smart course registration assistant for Duke Kunshan University (DKU), featuring course recommendation, prerequisite checking, schedule generation, and seat monitoring.
# CoursePilot: AI-Powered Smart Registration for DKU

CoursePilot is an AI-powered smart course registration assistant designed for Duke Kunshan University (DKU) students.

It helps students make better enrollment decisions by combining course recommendation, prerequisite checking, schedule generation, and seat monitoring into one system. The goal is to reduce the complexity of course registration and provide a more personalized, data-driven planning experience.

## Features
- Smart course recommendation based on major requirements, graduation progress, GPA, difficulty, and seat availability
- Prerequisite and corequisite checking
- Multiple schedule generation strategies: safe, interest-based, and balanced
- Time conflict detection and schedule health analysis
- Seat monitoring history with CSV export support

## Tech Stack
- Python
- FastAPI
- Pydantic
- JSON local data storage

## Use Case
CoursePilot is built for DKU students who need to balance academic requirements, personal interests, class availability, and timetable constraints during registration.

## Future Improvements
- Frontend dashboard for students
- Real-time seat monitoring and notifications
- Better personalization with user preferences
- Integration with official course bulletin / registration systems

## Running the Project

### 1. Install dependencies

```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the server

```bash
uvicorn main:app --reload
```

### 3. Open the API docs

```text
http://127.0.0.1:8000/docs
```

## Current Limitations

* Data is stored locally in JSON files rather than a database
* The seat-monitor router is implemented but not mounted in `main.py`
* Some modules overlap in purpose, and the codebase could be further unified and cleaned up
* Major matching depends on standardized major names in input data   
