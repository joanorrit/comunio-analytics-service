from fastapi import FastAPI, Depends, HTTPException
from .database import engine
from . import models
from .endpoints import admin, public

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(admin.router)
app.include_router(public.router)


@app.get("/")
def read_root():
    return {"API to get extra data from Biwenger"}
