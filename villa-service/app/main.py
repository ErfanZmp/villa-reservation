from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .routers import villas
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

models.Base.metadata.create_all(bind=models.engine)

app.include_router(villas.router, prefix="/villas")

@app.get("/")
def read_root():
    return {"message": "Villa Service"}