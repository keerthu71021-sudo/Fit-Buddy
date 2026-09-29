import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE_PATH = Path(
    os.getenv("FITBUDDY_DB_PATH")
    or Path(__file__).resolve().parent.parent / "fitbuddy.db"
)


@contextmanager
def connect():
    """Open a connection, commit on success, always close."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                height_cm REAL NOT NULL,
                weight_kg REAL NOT NULL,
                goal TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fitness_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                name TEXT NOT NULL,
                plan TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def create_profile(name: str, age: int, height_cm: float, weight_kg: float, goal: str) -> dict:
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO profiles (name, age, height_cm, weight_kg, goal) VALUES (?, ?, ?, ?, ?)",
            (name, age, height_cm, weight_kg, goal),
        )
        profile_id = cursor.lastrowid
    return get_profile(profile_id)


def get_profile(profile_id: int) -> dict | None:
    with connect() as connection:
        row = connection.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    return dict(row) if row else None


def save_fitness_plan(profile_id: int, name: str, plan: str) -> int:
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO fitness_plans (profile_id, name, plan) VALUES (?, ?, ?)",
            (profile_id, name, plan),
        )
        return cursor.lastrowid


def get_latest_fitness_plan(profile_id: int) -> str | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT plan FROM fitness_plans WHERE profile_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 1",
            (profile_id,),
        ).fetchone()
    return row["plan"] if row else None


def save_feedback(profile_id: int | None, rating: int, message: str) -> int:
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO feedback (profile_id, rating, message) VALUES (?, ?, ?)",
            (profile_id, rating, message),
        )
        return cursor.lastrowid


def get_profiles_with_feedback() -> list[dict]:
    with connect() as connection:
        profiles = connection.execute(
            "SELECT id, name, age, height_cm, weight_kg, goal, created_at "
            "FROM profiles ORDER BY created_at DESC, id DESC"
        ).fetchall()
        feedback_rows = connection.execute(
            "SELECT id, profile_id, rating, message, created_at "
            "FROM feedback ORDER BY created_at DESC, id DESC"
        ).fetchall()

    feedback_by_profile: dict[int, list[dict]] = {}
    for row in feedback_rows:
        feedback_by_profile.setdefault(row["profile_id"], []).append(dict(row))

    return [{**dict(p), "feedback": feedback_by_profile.get(p["id"], [])} for p in profiles]
