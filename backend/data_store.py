import os
import sqlite3

from models import AchievementMark

DB_PATH = os.getenv("DB_PATH", "user_achievements.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS achievement_marks (
                steam_id         TEXT NOT NULL,
                app_id           INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                status           TEXT NOT NULL,
                PRIMARY KEY (steam_id, app_id, achievement_name)
            )
            """
        )
        conn.commit()


def get_marks(steam_id: str, app_id: int) -> list[AchievementMark]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM achievement_marks WHERE steam_id = ? AND app_id = ?",
            (steam_id, app_id),
        ).fetchall()
    return [
        AchievementMark(
            steam_id=row["steam_id"],
            app_id=row["app_id"],
            achievement_name=row["achievement_name"],
            status=row["status"],
        )
        for row in rows
    ]


def set_mark(mark: AchievementMark) -> AchievementMark:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO achievement_marks (steam_id, app_id, achievement_name, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(steam_id, app_id, achievement_name) DO UPDATE SET status = excluded.status
            """,
            (mark.steam_id, mark.app_id, mark.achievement_name, mark.status),
        )
        conn.commit()
        row_id = cursor.lastrowid
    return AchievementMark(
        id=row_id,
        steam_id=mark.steam_id,
        app_id=mark.app_id,
        achievement_name=mark.achievement_name,
        status=mark.status,
    )


def delete_mark(steam_id: str, app_id: int, achievement_name: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM achievement_marks WHERE steam_id = ? AND app_id = ? AND achievement_name = ?",
            (steam_id, app_id, achievement_name),
        )
        conn.commit()
    return cursor.rowcount > 0
