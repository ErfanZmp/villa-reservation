from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .routers import reservations, admin
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="Reservation Service",
    description="Manages villa reservations, including creation and retrieval",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "reservations",
            "description": "Endpoints for managing villa reservations"
        },
        {
            "name": "admin",
            "description": "Admin endpoints for managing reservations"
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

app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
app.include_router(admin.router, prefix="/reservations/admin", tags=["admin"])

@app.get("/", tags=["root"], summary="Root Endpoint of the Reservation Service")
def read_root():
    return {"message": "Reservation Service"}