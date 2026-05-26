import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import steam_api
from models import GameAchievements, PlayerAchievements


MOCK_SCHEMA_RESPONSE = {
    "game": {
        "gameName": "Test Game",
        "availableGameStats": {
            "achievements": [
                {
                    "name": "ACH_WIN_ONE",
                    "displayName": "Win One Game",
                    "description": "Win your first game",
                },
                {
                    "name": "ACH_WIN_100",
                    "displayName": "Win 100 Games",
                    "description": "Win 100 games",
                },
            ]
        },
    }
}

MOCK_PERCENT_RESPONSE = {
    "achievementpercentages": {
        "achievements": [
            {"name": "ACH_WIN_ONE", "percent": 75.5},
            {"name": "ACH_WIN_100", "percent": 12.3},
        ]
    }
}

MOCK_PLAYER_RESPONSE = {
    "playerstats": {
        "achievements": [
            {
                "apiname": "ACH_WIN_ONE",
                "achieved": 1,
            },
            {
                "apiname": "ACH_WIN_100",
                "achieved": 0,
            },
        ]
    }
}


def make_mock_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@patch("steam_api.httpx.get")
def test_get_game_achievements_returns_correct_structure(mock_get):
    mock_get.side_effect = [
        make_mock_response(MOCK_SCHEMA_RESPONSE),
        make_mock_response(MOCK_PERCENT_RESPONSE),
    ]

    result = steam_api.get_game_achievements(app_id=12345)

    assert isinstance(result, GameAchievements)
    assert result.game_name == "Test Game"
    assert result.app_id == 12345
    assert len(result.achievements) == 2


@patch("steam_api.httpx.get")
def test_achievements_sorted_by_difficulty(mock_get):
    mock_get.side_effect = [
        make_mock_response(MOCK_SCHEMA_RESPONSE),
        make_mock_response(MOCK_PERCENT_RESPONSE),
    ]

    result = steam_api.get_game_achievements(app_id=12345)
    percents = [a.global_percent for a in result.achievements]

    assert percents == sorted(percents), "Achievements skal sorteres fra sværest til lettest"


@patch("steam_api.httpx.get")
def test_get_game_achievements_combines_schema_and_percents(mock_get):
    mock_get.side_effect = [
        make_mock_response(MOCK_SCHEMA_RESPONSE),
        make_mock_response(MOCK_PERCENT_RESPONSE),
    ]

    result = steam_api.get_game_achievements(app_id=12345)

    assert result.achievements[0].name == "ACH_WIN_100"
    assert result.achievements[0].global_percent == 12.3
    assert result.achievements[0].display_name == "Win 100 Games"

    assert result.achievements[1].name == "ACH_WIN_ONE"
    assert result.achievements[1].global_percent == 75.5


@patch("steam_api.httpx.get")
def test_get_player_achievements_returns_correct_structure(mock_get):
    mock_get.side_effect = [
        make_mock_response(MOCK_SCHEMA_RESPONSE),
        make_mock_response(MOCK_PERCENT_RESPONSE),
        make_mock_response(MOCK_PLAYER_RESPONSE),
    ]

    result = steam_api.get_player_achievements(steam_id="76561198000000001", app_id=12345)

    assert isinstance(result, PlayerAchievements)
    assert result.steam_id == "76561198000000001"
    assert result.game_name == "Test Game"
    assert len(result.achievements) == 2


@patch("steam_api.httpx.get")
def test_get_player_achievements_correct_unlock_status(mock_get):
    mock_get.side_effect = [
        make_mock_response(MOCK_SCHEMA_RESPONSE),
        make_mock_response(MOCK_PERCENT_RESPONSE),
        make_mock_response(MOCK_PLAYER_RESPONSE),
    ]

    result = steam_api.get_player_achievements(steam_id="76561198000000001", app_id=12345)

    achieved = {a.name: a.achieved for a in result.achievements}
    assert achieved["ACH_WIN_ONE"] is True
    assert achieved["ACH_WIN_100"] is False


@patch("steam_api.httpx.get")
def test_get_player_achievements_enriched_with_global_percent(mock_get):
    mock_get.side_effect = [
        make_mock_response(MOCK_SCHEMA_RESPONSE),
        make_mock_response(MOCK_PERCENT_RESPONSE),
        make_mock_response(MOCK_PLAYER_RESPONSE),
    ]

    result = steam_api.get_player_achievements(steam_id="76561198000000001", app_id=12345)

    percents = {a.name: a.global_percent for a in result.achievements}
    assert percents["ACH_WIN_ONE"] == 75.5
    assert percents["ACH_WIN_100"] == 12.3
