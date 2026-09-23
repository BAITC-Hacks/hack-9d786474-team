from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from .database import Base, engine
from .database import SessionLocal
from .seed import seed_demo_data
from .routers.tasks import router as tasks_router
from .routers.catalog import router as catalog_router
from .routers.teams import router as teams_router
from .routers.proposals import router as proposals_router, task_proposals_router
from .routers.profiles import router as profiles_router

Base.metadata.create_all(bind=engine)
if engine.dialect.name == "sqlite":
    # create_all does not add columns to an existing demo database.
    with engine.begin() as connection:
        team_columns = {column["name"] for column in inspect(connection).get_columns("teams")}
        for column in ("interests", "skills", "technologies"):
            if column not in team_columns:
                connection.execute(text(f"ALTER TABLE teams ADD COLUMN {column} JSON NOT NULL DEFAULT '[]'"))
with SessionLocal() as seed_db:
    seed_demo_data(seed_db)
app = FastAPI(title="BAITC Hacks Task Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tasks_router)
app.include_router(catalog_router)
app.include_router(teams_router)
app.include_router(proposals_router)
app.include_router(task_proposals_router)
app.include_router(profiles_router)

@app.get("/health")
def health():
    return {"status": "ok"}
