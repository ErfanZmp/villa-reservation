from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .dependencies import get_db, create_access_token, get_current_user
from .routers import auth, users
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

models.Base.metadata.create_all(bind=models.engine)

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")

@app.get("/")
def read_root():
    return {"message": "User Service"}