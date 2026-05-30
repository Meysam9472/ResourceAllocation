# University Timetable Scheduler 🎓🕒

A robust backend system built with FastAPI for automating and managing university course scheduling. The system uses Google OR-Tools to solve the complex timetable constraint programming problem in the background using Celery and Redis. 

It features a dual-database architecture: PostgreSQL for relational data (Users, Courses, Teachers) and MongoDB for storing the generated schedule results.

## 🚀 Features

*   **Algorithmic Scheduling**: Automated timetable generation using Google OR-Tools.
*   **Asynchronous Processing**: Heavy scheduling tasks are offloaded to background workers using Celery and Redis.
*   **Dual Database Architecture**: 
    *   **PostgreSQL**: Manages structured data (Users, Teachers, Courses) via SQLAlchemy ORM.
    *   **MongoDB**: Stores the generated, unstructured schedule outputs.
*   **Authentication & Authorization**: Secure JWT-based login (Access & Refresh tokens) with Argon2 password hashing.
*   **Role-Based Access Control (RBAC)**: Distinct permissions for Super Admins, Admins, and Normal Users.
*   **Database Migrations**: Handled seamlessly with Alembic.

## 🛠️ Tech Stack

*   **Framework**: FastAPI
*   **Task Queue**: Celery
*   **Message Broker / Result Backend**: Redis
*   **Relational Database**: PostgreSQL (asyncpg)
*   **NoSQL Database**: MongoDB (motor/pymongo)
*   **ORM**: SQLAlchemy (Async)
*   **Migrations**: Alembic
*   **Security**: Passlib (Argon2), python-jose (JWT)
*   **Solver**: Google OR-Tools

## 📁 Project Structure

```text
├── alembic/                # Database migration scripts
├── core/
│   ├── security.py         # JWT and password hashing (Argon2)
│   ├── dependencies.py     # FastAPI dependencies (Auth, DB session)
├── database/
│   ├── database_pg.py      # PostgreSQL async engine and session
│   ├── database_mongo.py   # MongoDB connection manager
├── models/                 # SQLAlchemy models (User, Teacher, Course)
├── routers/                # FastAPI endpoint routers (users, auth, schedule)
├── schemas/                # Pydantic models for validation
├── services/
│   ├── scheduler.py        # OR-Tools timetable logic
├── celery_worker.py        # Celery app configuration
├── tasks.py                # Celery background tasks
├── main.py                 # FastAPI application entry point
├── alembic.ini             # Alembic configuration
└── requirements.txt        # Python dependencies
```

## ⚙️ Prerequisites

*   Python 3.10+
*   PostgreSQL
*   MongoDB
*   Redis

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/university-timetable-scheduler.git
   cd university-timetable-scheduler
   ```

2. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup:**
   Ensure PostgreSQL, MongoDB, and Redis are running. Update your connection strings in the code or `.env` file accordingly.

5. **Run Migrations (PostgreSQL):**
   ```bash
   alembic upgrade head
   ```

## 🏃‍♂️ Running the Application

You need to run three separate processes for the application to work fully:

1. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Start the Celery worker (Linux/macOS):**
   ```bash
   celery -A celery_worker.celery_app worker --loglevel=info
   ```
   *(Note for Windows users: Use `celery -A celery_worker.celery_app worker --loglevel=info -P solo`)*

## 📡 Key API Endpoints

**Authentication & Users**
*   `POST /login` - Get JWT access and refresh tokens.
*   `POST /users/` - Create a new user.
*   `GET /users/` - List all users (Admin only).
*   `DELETE /users/{id}` - Delete a user (Admin only).

**Scheduling**
*   `POST /schedule/start` - Trigger the background timetable generation task.
*   `GET /schedule/status/{task_id}` - Check the status of the scheduling task.

*Check the auto-generated Swagger UI at `http://127.0.0.1:8000/docs` for the complete API documentation once the server is running.*
