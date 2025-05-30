from fastapi import FastAPI
from . import models
from .routers import reservations
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
        }
    ]
)

models.Base.metadata.create_all(bind=models.engine)

app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])

@app.get("/", tags=["root"], summary="Root Endpoint of the Reservation Service")
def read_root():
    return {"message": "Reservation Service"}