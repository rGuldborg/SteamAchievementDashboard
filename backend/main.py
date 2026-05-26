from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

import steam_api
import llm
import data_store
from models import UserAchievement, AchievementMark


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_store.init_db()
    yield


app = FastAPI(
    title="Steam Achievement Dashboard API",
    description="Backend API til Steam Achievement Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/player/{steam_id}/games")
def get_owned_games(steam_id: str):
    try:
        return steam_api.get_owned_games(steam_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/achievements/{app_id}")
def get_achievements(app_id: int):
    try:
        return steam_api.get_game_achievements(app_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/player/{steam_id}/{app_id}/achievements")
def get_player_achievements(steam_id: str, app_id: int):
    try:
        return steam_api.get_player_achievements(steam_id, app_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/player/{steam_id}/{app_id}/estimate")
def get_llm_estimate(steam_id: str, app_id: int):
    try:
        game_data = steam_api.get_game_achievements(app_id)
        estimate = llm.estimate_completion_time(game_data.achievements)
        return estimate
    except Exception as e:
        print(f"ESTIMATE ERROR: {e}", flush=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/marks/{steam_id}/{app_id}")
def get_marks(steam_id: str, app_id: int):
    return data_store.get_marks(steam_id, app_id)


@app.post("/marks", status_code=201)
def set_mark(mark: AchievementMark):
    data_store.set_mark(mark)
    return {"ok": True}


@app.delete("/marks/{steam_id}/{app_id}/{achievement_name}")
def delete_mark(steam_id: str, app_id: int, achievement_name: str):
    data_store.delete_mark(steam_id, app_id, achievement_name)
    return {"ok": True}


@app.get("/user-achievements")
def get_user_achievements():
    return data_store.get_all_achievements()


@app.post("/user-achievements", status_code=201)
def add_user_achievement(achievement: UserAchievement):
    return data_store.add_achievement(achievement)


@app.patch("/user-achievements/{achievement_id}")
def toggle_user_achievement(achievement_id: int, achieved: bool):
    success = data_store.update_achievement(achievement_id, achieved)
    if not success:
        raise HTTPException(status_code=404, detail="Achievement ikke fundet")
    return {"ok": True}


@app.delete("/user-achievements/{achievement_id}")
def delete_user_achievement(achievement_id: int):
    success = data_store.delete_achievement(achievement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Achievement ikke fundet")
    return {"ok": True}
