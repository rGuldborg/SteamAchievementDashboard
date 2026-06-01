from typing import Any

import requests
import streamlit as st

BACKEND_URL = "http://backend:8000"


def fetch_owned_games(steam_id: str) -> list[dict[str, Any]]:
    try:
        resp = requests.get(f"{BACKEND_URL}/player/{steam_id}/games", timeout=15)
        resp.raise_for_status()
        games: list[dict[str, Any]] = resp.json()
        return games
    except Exception as e:
        st.error(f"Kunne ikke hente spil for profilen: {e}")
        return []


def fetch_player_achievements(steam_id: str, app_id: int) -> dict[str, Any] | None:
    try:
        resp = requests.get(
            f"{BACKEND_URL}/player/{steam_id}/{app_id}/achievements", timeout=20
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        return data
    except Exception as e:
        st.error(f"Kunne ikke hente achievements: {e}")
        return None


def fetch_llm_estimate(steam_id: str, app_id: int) -> dict[str, Any] | None:
    try:
        resp = requests.get(
            f"{BACKEND_URL}/player/{steam_id}/{app_id}/estimate", timeout=60
        )
        resp.raise_for_status()
        estimate: dict[str, Any] = resp.json()
        return estimate
    except Exception as e:
        st.error(f"Kunne ikke hente LLM-estimat: {e}")
        return None


def fetch_marks(steam_id: str, app_id: int) -> list[dict[str, Any]]:
    try:
        resp = requests.get(f"{BACKEND_URL}/marks/{steam_id}/{app_id}", timeout=10)
        resp.raise_for_status()
        marks: list[dict[str, Any]] = resp.json()
        return marks
    except Exception:
        return []


def set_mark(steam_id: str, app_id: int, achievement_name: str, status: str) -> bool:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/marks",
            json={
                "steam_id": steam_id,
                "app_id": app_id,
                "achievement_name": achievement_name,
                "status": status,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Kunne ikke gemme markering: {e}")
        return False


def delete_mark(steam_id: str, app_id: int, achievement_name: str) -> None:
    try:
        requests.delete(
            f"{BACKEND_URL}/marks/{steam_id}/{app_id}/{achievement_name}", timeout=10
        )
    except Exception:
        pass
