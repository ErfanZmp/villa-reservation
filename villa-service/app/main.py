from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .routers import villas
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="Villa Service",
    description="Manages villa creation, updates, and retrieval",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "villas",
            "description": "Endpoints for managing villa data and images"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=models.engine)

app.include_router(villas.router, prefix="/villas", tags=["villas"])

@app.get("/", tags=["root"], summary="Root Endpoint of the Villa Service")
def read_root():
    return {"message": "Villa Service"}