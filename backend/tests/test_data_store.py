import os
import sys
from collections.abc import Iterator
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import data_store
from models import AchievementMark


@pytest.fixture(autouse=True)
def use_temp_db() -> Iterator[None]:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_file = f.name
    with patch.object(data_store, "DB_PATH", db_file):
        data_store.init_db()
        yield
    os.unlink(db_file)


def make_mark(achievement_name: str = "ACH_WIN_ONE", status: str = "mål") -> AchievementMark:
    return AchievementMark(
        steam_id="76561198000000001",
        app_id=12345,
        achievement_name=achievement_name,
        status=status,
    )


def test_set_and_get_mark() -> None:
    mark = make_mark("ACH_WIN_ONE", "mål")
    saved = data_store.set_mark(mark)

    assert saved.id is not None
    assert saved.achievement_name == "ACH_WIN_ONE"
    assert saved.status == "mål"

    marks = data_store.get_marks("76561198000000001", 12345)
    assert len(marks) == 1
    assert marks[0].achievement_name == "ACH_WIN_ONE"
    assert marks[0].status == "mål"


def test_set_mark_overwrites_existing() -> None:
    data_store.set_mark(make_mark("ACH_WIN_ONE", "mål"))
    data_store.set_mark(make_mark("ACH_WIN_ONE", "i gang"))

    marks = data_store.get_marks("76561198000000001", 12345)
    assert len(marks) == 1
    assert marks[0].status == "i gang"


def test_get_marks_returns_only_correct_player_and_game() -> None:
    data_store.set_mark(make_mark("ACH_WIN_ONE", "mål"))

    data_store.set_mark(AchievementMark(
        steam_id="76561198999999999",
        app_id=12345,
        achievement_name="ACH_WIN_ONE",
        status="i gang",
    ))

    data_store.set_mark(AchievementMark(
        steam_id="76561198000000001",
        app_id=99999,
        achievement_name="ACH_WIN_ONE",
        status="mål",
    ))

    marks = data_store.get_marks("76561198000000001", 12345)
    assert len(marks) == 1
    assert marks[0].achievement_name == "ACH_WIN_ONE"


def test_delete_mark() -> None:
    data_store.set_mark(make_mark("ACH_WIN_ONE", "mål"))

    success = data_store.delete_mark("76561198000000001", 12345, "ACH_WIN_ONE")
    assert success is True

    marks = data_store.get_marks("76561198000000001", 12345)
    assert len(marks) == 0


def test_delete_nonexistent_mark() -> None:
    success = data_store.delete_mark("76561198000000001", 12345, "ACH_DOES_NOT_EXIST")
    assert success is False


def test_multiple_marks_same_game() -> None:
    data_store.set_mark(make_mark("ACH_WIN_ONE", "mål"))
    data_store.set_mark(make_mark("ACH_WIN_100", "i gang"))
    data_store.set_mark(make_mark("ACH_SPEEDRUN", "mål"))

    marks = data_store.get_marks("76561198000000001", 12345)
    assert len(marks) == 3

    statuses = {m.achievement_name: m.status for m in marks}
    assert statuses["ACH_WIN_ONE"] == "mål"
    assert statuses["ACH_WIN_100"] == "i gang"
    assert statuses["ACH_SPEEDRUN"] == "mål"
