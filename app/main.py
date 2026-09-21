from fastapi import FastAPI
from app.database import engine
from app.routes import router
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

@asynccontextmanager
async def lifespan(app:FastAPI):
	SQLModel.metadata.create_all(engine)
	yield

app=FastAPI(lifespan=lifespan)
app.include_router(router)