import sqlite3
from models import UserAchievement, AchievementMark

DB_PATH = "user_achievements.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_achievements (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                title   TEXT NOT NULL,
                note    TEXT NOT NULL DEFAULT '',
                achieved INTEGER NOT NULL DEFAULT 0
            )
            """
        )
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


def get_all_achievements() -> list[UserAchievement]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM user_achievements").fetchall()
    return [
        UserAchievement(
            id=row["id"],
            title=row["title"],
            note=row["note"],
            achieved=bool(row["achieved"]),
        )
        for row in rows
    ]


def add_achievement(achievement: UserAchievement) -> UserAchievement:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO user_achievements (title, note, achieved) VALUES (?, ?, ?)",
            (achievement.title, achievement.note, int(achievement.achieved)),
        )
        conn.commit()
        new_id = cursor.lastrowid

    return UserAchievement(
        id=new_id,
        title=achievement.title,
        note=achievement.note,
        achieved=achievement.achieved,
    )


def update_achievement(achievement_id: int, achieved: bool) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE user_achievements SET achieved = ? WHERE id = ?",
            (int(achieved), achievement_id),
        )
        conn.commit()
    return cursor.rowcount > 0


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


def set_mark(mark: AchievementMark) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO achievement_marks (steam_id, app_id, achievement_name, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(steam_id, app_id, achievement_name) DO UPDATE SET status = excluded.status
            """,
            (mark.steam_id, mark.app_id, mark.achievement_name, mark.status),
        )
        conn.commit()


def delete_mark(steam_id: str, app_id: int, achievement_name: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM achievement_marks WHERE steam_id = ? AND app_id = ? AND achievement_name = ?",
            (steam_id, app_id, achievement_name),
        )
        conn.commit()


def delete_achievement(achievement_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM user_achievements WHERE id = ?",
            (achievement_id,),
        )
        conn.commit()
    return cursor.rowcount > 0
