from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .routers import auth, users
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="User Service",
    description="Manages user authentication and registration",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Endpoints for user login, registration, and verification"
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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/", tags=["root"], summary="Root Endpoint of the User Service")
def read_root():
    return {"message": "User Service"}