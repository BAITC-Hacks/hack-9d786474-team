from fastapi import FastAPI
from .database import Base, engine
from .routers.tasks import router as tasks_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="BAITC Hacks Task Platform API")
app.include_router(tasks_router)

@app.get("/health")
def health():
    return {"status": "ok"}
