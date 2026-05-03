from pydantic import BaseModel

class TeamCreate(BaseModel):
    name: str
    sport: str

class TeamResponse(BaseModel):
    id: int
    name: str
    sport: str

    class Config:
        from_attributes = True

class GameCreate(BaseModel):
    home_team_id: int
    away_team_id: int
    home_score: int
    away_score: int
