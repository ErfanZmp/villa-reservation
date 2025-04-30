from fastapi import FastAPI
from . import models
from .routers import villas
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

models.Base.metadata.create_all(bind=models.engine)

app.include_router(villas.router, prefix="/villas", tags=["villas"])

@app.get("/", tags=["root"], summary="Root Endpoint of the Villa Service")
def read_root():
    return {"message": "Villa Service"}