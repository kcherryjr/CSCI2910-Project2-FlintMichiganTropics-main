from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from API_Handeling import models, schemas
from API_Handeling.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/teams")
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    db_team = models.Team(name=team.name, sport=team.sport)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/teams")
def get_teams(db: Session = Depends(get_db)):
    return db.query(models.Team).all()

@app.post("/games")
def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    db_game = models.Game(
        home_team_id=game.home_team_id,
        away_team_id=game.away_team_id,
        home_score=game.home_score,
        away_score=game.away_score
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


@app.get("/games")
def get_games(db: Session = Depends(get_db)):
    return db.query(models.Game).all()

@app.get("/games/live/{team_id}")
def get_live_game(team_id: int, db: Session = Depends(get_db)):
    game = db.query(models.Game)\
        .filter(
            (models.Game.home_team_id == team_id) |
            (models.Game.away_team_id == team_id)
        )\
        .order_by(models.Game.id.desc())\
        .first()

    if not game:
        return {"message": "No game found"}

    return game