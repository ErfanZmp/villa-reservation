from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import SessionLocal
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
VILLA_SERVICE_URL = os.getenv("VILLA_SERVICE_URL")
bearer_scheme = HTTPBearer(scheme_name="BearerAuth", description="Enter the JWT token obtained from /auth/login/verify")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/profile", headers={"Authorization": f"Bearer {credentials.credentials}"})
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return response.json()

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/profile", headers={"Authorization": f"Bearer {credentials.credentials}"})
        if response.status_code != 200 or response.json().get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        return response.json()