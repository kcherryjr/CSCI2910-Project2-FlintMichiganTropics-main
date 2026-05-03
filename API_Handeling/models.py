from sqlalchemy import Column, Integer, String
from API_Handeling.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    sport = Column(String)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer)
    away_team_id = Column(Integer)
    home_score = Column(Integer)
    away_score = Column(Integer)