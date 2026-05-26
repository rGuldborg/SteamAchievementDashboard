from pydantic import BaseModel


class Achievement(BaseModel):
    name: str
    display_name: str
    description: str
    global_percent: float
    achieved: bool = False


class GameAchievements(BaseModel):
    app_id: int
    game_name: str
    achievements: list[Achievement]


class PlayerAchievements(BaseModel):
    steam_id: str
    app_id: int
    achievements: list[Achievement]


class OwnedGame(BaseModel):
    app_id: int
    name: str
    playtime_hours: float


class UserAchievement(BaseModel):
    id: int | None = None
    title: str
    note: str
    achieved: bool = False


class LLMEstimate(BaseModel):
    estimated_hours: str
    reasoning: str


class AchievementMark(BaseModel):
    steam_id: str
    app_id: int
    achievement_name: str
    status: str
