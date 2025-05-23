from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import User
from ..dependencies import get_db, get_password_hash, create_access_token
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
OTP_SERVICE_URL = os.getenv("OTP_SERVICE_URL")
router = APIRouter()

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    national_code: str
    phone_number: str
    password: str

class SignupVerifyRequest(BaseModel):
    phone_number: str
    otp: str

class LoginRequest(BaseModel):
    phone_number: str

class LoginVerifyRequest(BaseModel):
    phone_number: str
    otp: str

@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone_number == request.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    if db.query(User).filter(User.national_code == request.national_code).first():
        raise HTTPException(status_code=400, detail="National code already registered")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OTP_SERVICE_URL}/otp/generate", json={"phone_number": request.phone_number})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to generate OTP")
    return {"message": "OTP sent to phone number", "otp_response": response.json()}

@router.post("/signup/verify")
async def signup_verify(request: SignupVerifyRequest, signup_data: SignupRequest, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OTP_SERVICE_URL}/otp/validate", json={"phone_number": request.phone_number, "otp": request.otp})
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid OTP")
    hashed_password = get_password_hash(signup_data.password)
    user = User(
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        national_code=signup_data.national_code,
        phone_number=signup_data.phone_number,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OTP_SERVICE_URL}/otp/generate", json={"phone_number": request.phone_number})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to generate OTP")
    return {"message": "OTP sent to phone number", "otp_response": response.json()}

@router.post("/login/verify")
async def login_verify(request: LoginVerifyRequest, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OTP_SERVICE_URL}/otp/validate", json={"phone_number": request.phone_number, "otp": request.otp})
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid OTP")
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}