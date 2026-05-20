# API Testing Guide

This document contains `curl` commands to test the FastAPI scheduling endpoints. Ensure your FastAPI server, Redis, and Celery workers are running before executing these tests.

## 1. Start the Scheduling Task

Send a `POST` request to start the background scheduling task with sample data.
```bash
curl -X 'POST' \
  'http://localhost:8000/schedule/start' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "teachers": {
        "T1": {"name": "Prof. A","teacher_available_times":[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},                                           
        "T2": {"name": "Prof. B","teacher_available_times":[0, 1, 2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19]},  
        "T3": {"name": "Prof. C","teacher_available_times":[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
        "T4": {"name": "Prof. D","teacher_available_times":[2, 3, 4, 5, 6, 7, 10, 11, 14, 15, 16, 17, 18, 19]},                                           
        "T5": {"name": "Prof. E","teacher_available_times":[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
        "T6": {"name": "Prof. F","teacher_available_times":[0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17]}, 
        "T7": {"name": "Prof. G","teacher_available_times":[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}
    },
  "courses": {

        "C26_1":  {"name": "C26_Course_1", "cohort": "2026", "credits": 3, "teachers": ["T1"]},
        "C26_2":  {"name": "C26_Course_2", "cohort": "2026", "credits": 3, "teachers": ["T4"]},
        "C26_3":  {"name": "C26_Course_3", "cohort": "2026", "credits": 1, "teachers": ["T1"]},
        "C26_4":  {"name": "C26_Course_4", "cohort": "2026", "credits": 2, "teachers": ["T7"]},
        "C26_5":  {"name": "C26_Course_5", "cohort": "2026", "credits": 3, "teachers": ["T2"]},
        "C26_6":  {"name": "C26_Course_6", "cohort": "2026", "credits": 1, "teachers": ["T2"]},
        "C26_7":  {"name": "C26_Course_7", "cohort": "2026", "credits": 2, "teachers": ["T3"]},
        "C26_8":  {"name": "C26_Course_8", "cohort": "2026", "credits": 3, "teachers": ["T4"]},
        "C26_9":  {"name": "C26_Course_9", "cohort": "2026", "credits": 1, "teachers": ["T5"]},
        "C26_10": {"name": "C26_Course_10", "cohort": "2026", "credits": 2, "teachers": ["T7"]},

        "C25_1":  {"name": "C25_Course_1", "cohort": "2025", "credits": 3, "teachers": ["T1"]},
        "C25_2":  {"name": "C25_Course_2", "cohort": "2025", "credits": 3, "teachers": ["T2"]},
        "C25_3":  {"name": "C25_Course_3", "cohort": "2025", "credits": 2, "teachers": ["T4"]},
        "C25_4":  {"name": "C25_Course_4", "cohort": "2025", "credits": 1, "teachers": ["T5"]},
        "C25_5":  {"name": "C25_Course_5", "cohort": "2025", "credits": 3, "teachers": ["T7"]},
        "C25_6":  {"name": "C25_Course_6", "cohort": "2025", "credits": 2, "teachers": ["T1"]},
        "C25_7":  {"name": "C25_Course_7", "cohort": "2025", "credits": 1, "teachers": ["T2"]},
        "C25_8":  {"name": "C25_Course_8", "cohort": "2025", "credits": 3, "teachers": ["T3"]},
        "C25_9":  {"name": "C25_Course_9", "cohort": "2025", "credits": 2, "teachers": ["T6"]},
        "C25_10": {"name": "C25_Course_10", "cohort": "2025", "credits": 1, "teachers": ["T7"]},

        "C24_1":  {"name": "C24_Course_1", "cohort": "2024", "credits": 3, "teachers": ["T3"]},
        "C24_2":  {"name": "C24_Course_2", "cohort": "2024", "credits": 3, "teachers": ["T4"]},
        "C24_3":  {"name": "C24_Course_3", "cohort": "2024", "credits": 2, "teachers": ["T5"]},
        "C24_4":  {"name": "C24_Course_4", "cohort": "2024", "credits": 1, "teachers": ["T6"]},
        "C24_5":  {"name": "C24_Course_5", "cohort": "2024", "credits": 3, "teachers": ["T2"]},
        "C24_6":  {"name": "C24_Course_6", "cohort": "2024", "credits": 2, "teachers": ["T3"]},
        "C24_7":  {"name": "C24_Course_7", "cohort": "2024", "credits": 1, "teachers": ["T1"]},
        "C24_8":  {"name": "C24_Course_8", "cohort": "2024", "credits": 3, "teachers": ["T4"]},
        "C24_9":  {"name": "C24_Course_9", "cohort": "2024", "credits": 2, "teachers": ["T5"]},
        "C24_10": {"name": "C24_Course_10", "cohort": "2024", "credits": 1, "teachers": ["T2"]},

        "C23_1":  {"name": "C23_Course_1", "cohort": "2023", "credits": 3, "teachers": ["T6"]},
        "C23_2":  {"name": "C23_Course_2", "cohort": "2023", "credits": 3, "teachers": ["T7"]},
        "C23_3":  {"name": "C23_Course_3", "cohort": "2023", "credits": 2, "teachers": ["T1"]},
        "C23_4":  {"name": "C23_Course_4", "cohort": "2023", "credits": 1, "teachers": ["T2"]},
        "C23_5":  {"name": "C23_Course_5", "cohort": "2023", "credits": 3, "teachers": ["T4"]},
        "C23_6":  {"name": "C23_Course_6", "cohort": "2023", "credits": 2, "teachers": ["T5"]},
        "C23_7":  {"name": "C23_Course_7", "cohort": "2023", "credits": 1, "teachers": ["T6"]},
        "C23_8":  {"name": "C23_Course_8", "cohort": "2023", "credits": 3, "teachers": ["T7"]},
        "C23_9":  {"name": "C23_Course_9", "cohort": "2023", "credits": 2, "teachers": ["T3"]},
        "C23_10": {"name": "C23_Course_10", "cohort": "2023", "credits": 1, "teachers": ["T4"]}
    },
  "num_rooms": 3,
  "cohorts": ["2023", "2024", "2025", "2026"],
  "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
  "hours": ["8:00 AM", "10:00 AM", "14:00 PM", "16:00 PM"]
}'

**Expected Response:**
You will receive a `task_id` which is required for the next step.

json
{
  "task_id": "b9e6c4f0-7b5a-4b9e-9b0a-1c2d3e4f5a6b",
  "message": "Background processing started."
}

---

## 2. Check Task Status

Use the `task_id` received from the previous request to check the status of your task. Replace `YOUR_TASK_ID` with the actual ID.

bash
curl -X 'GET' \
  'http://localhost:8000/schedule/status/YOUR_TASK_ID' \
  -H 'accept: application/json'

**Example:**

bash
curl -X 'GET' \
  'http://localhost:8000/schedule/status/b9e6c4f0-7b5a-4b9e-9b0a-1c2d3e4f5a6b' \
  -H 'accept: application/json'

**Expected Response (if completed successfully):**

json
{
  "status": "SUCCESS",
  "result": {
"status": "success",
"data": { ... scheduled data ... }
  }
}

**Expected Response (if still processing):**

json
{
  "status": "PENDING",
  "result": null
}
