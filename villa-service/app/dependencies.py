from fastapi import HTTPException, status
from .models import SessionLocal
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_admin(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/profile", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200 or response.json().get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        return response.json()