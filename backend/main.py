from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

import data_store
import llm
import steam_api
from models import (
    AchievementMark,
    GameAchievements,
    LLMEstimate,
    OwnedGame,
    PlayerAchievements,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    data_store.init_db()
    yield


app = FastAPI(
    title="Steam Achievement Dashboard API",
    description="Backend API til Steam Achievement Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/player/{steam_id}/games")
def get_owned_games(steam_id: str) -> list[OwnedGame]:
    try:
        return steam_api.get_owned_games(steam_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/achievements/{app_id}")
def get_achievements(app_id: int) -> GameAchievements:
    try:
        return steam_api.get_game_achievements(app_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/player/{steam_id}/{app_id}/achievements")
def get_player_achievements(steam_id: str, app_id: int) -> PlayerAchievements:
    try:
        return steam_api.get_player_achievements(steam_id, app_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/player/{steam_id}/{app_id}/estimate")
def get_llm_estimate(steam_id: str, app_id: int) -> LLMEstimate:
    try:
        game_data = steam_api.get_game_achievements(app_id)
        estimate = llm.estimate_completion_time(game_data.achievements)
        return estimate
    except Exception as e:
        print(f"ESTIMATE ERROR: {e}", flush=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/marks/{steam_id}/{app_id}")
def get_marks(steam_id: str, app_id: int) -> list[AchievementMark]:
    return data_store.get_marks(steam_id, app_id)


@app.post("/marks", status_code=201)
def set_mark(mark: AchievementMark) -> dict[str, bool]:
    data_store.set_mark(mark)
    return {"ok": True}


@app.delete("/marks/{steam_id}/{app_id}/{achievement_name}")
def delete_mark(steam_id: str, app_id: int, achievement_name: str) -> dict[str, bool]:
    data_store.delete_mark(steam_id, app_id, achievement_name)
    return {"ok": True}
