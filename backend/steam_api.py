import os
import httpx
from models import Achievement, GameAchievements, OwnedGame, PlayerAchievements

STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
STEAM_BASE_URL = "https://api.steampowered.com"


def get_owned_games(steam_id: str) -> list[OwnedGame]:
    url = f"{STEAM_BASE_URL}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1,
    }
    resp = httpx.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    raw_games = data.get("response", {}).get("games", [])

    games: list[OwnedGame] = []
    for g in raw_games:
        games.append(
            OwnedGame(
                app_id=g["appid"],
                name=g.get("name", f"App {g['appid']}"),
                playtime_hours=round(g.get("playtime_forever", 0) / 60, 1),
            )
        )

    games.sort(key=lambda g: g.playtime_hours, reverse=True)
    return games


def get_game_achievements(app_id: int) -> GameAchievements:
    schema_url = f"{STEAM_BASE_URL}/ISteamUserStats/GetSchemaForGame/v2/"
    schema_resp = httpx.get(schema_url, params={"key": STEAM_API_KEY, "appid": app_id})
    schema_resp.raise_for_status()
    schema_data = schema_resp.json()

    game_info = schema_data.get("game", {})
    game_name = game_info.get("gameName", f"App {app_id}")
    game_stats = game_info.get("availableGameStats", {})
    schema_achievements = game_stats.get("achievements", [])

    schema_map: dict[str, dict[str, str]] = {}
    for a in schema_achievements:
        schema_map[a["name"]] = {
            "display_name": a.get("displayName", a["name"]),
            "description": a.get("description", ""),
        }

    percent_url = f"{STEAM_BASE_URL}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
    percent_resp = httpx.get(percent_url, params={"gameid": app_id})
    percent_resp.raise_for_status()
    percent_data = percent_resp.json()

    raw_achievements = percent_data.get("achievementpercentages", {}).get("achievements", [])

    achievements: list[Achievement] = []
    for a in raw_achievements:
        name = a["name"]
        info = schema_map.get(name, {"display_name": name, "description": ""})
        achievements.append(
            Achievement(
                name=name,
                display_name=info["display_name"],
                description=info["description"],
                global_percent=round(float(a.get("percent", 0.0)), 2),
            )
        )

    achievements.sort(key=lambda x: x.global_percent)

    return GameAchievements(app_id=app_id, game_name=game_name, achievements=achievements)


def get_player_achievements(steam_id: str, app_id: int) -> PlayerAchievements:
    schema_url = f"{STEAM_BASE_URL}/ISteamUserStats/GetSchemaForGame/v2/"
    schema_resp = httpx.get(schema_url, params={"key": STEAM_API_KEY, "appid": app_id})
    schema_resp.raise_for_status()
    schema_data = schema_resp.json()

    game_info = schema_data.get("game", {})
    game_name = game_info.get("gameName", f"App {app_id}")
    schema_achievements = game_info.get("availableGameStats", {}).get("achievements", [])

    schema_map: dict[str, dict[str, str]] = {}
    for a in schema_achievements:
        schema_map[a["name"]] = {
            "display_name": a.get("displayName", a["name"]),
            "description": a.get("description", ""),
        }

    percent_url = f"{STEAM_BASE_URL}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
    percent_resp = httpx.get(percent_url, params={"gameid": app_id})
    percent_resp.raise_for_status()
    percent_map: dict[str, float] = {
        a["name"]: round(float(a.get("percent", 0.0)), 2)
        for a in percent_resp.json().get("achievementpercentages", {}).get("achievements", [])
    }

    player_url = f"{STEAM_BASE_URL}/ISteamUserStats/GetPlayerAchievements/v1/"
    player_resp = httpx.get(player_url, params={
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "appid": app_id,
        "l": "english",
    })
    player_resp.raise_for_status()
    raw_player = player_resp.json().get("playerstats", {}).get("achievements", [])

    achievements: list[Achievement] = []
    for a in raw_player:
        name = a["apiname"]
        info = schema_map.get(name, {"display_name": name, "description": ""})
        achievements.append(
            Achievement(
                name=name,
                display_name=info["display_name"],
                description=info["description"],
                global_percent=percent_map.get(name, 0.0),
                achieved=bool(a.get("achieved", 0)),
            )
        )

    achievements.sort(key=lambda x: (x.achieved, x.global_percent))

    return PlayerAchievements(
        steam_id=steam_id,
        app_id=app_id,
        game_name=game_name,
        achievements=achievements,
    )
