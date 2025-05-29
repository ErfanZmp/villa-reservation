from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .redis_client import redis_client
import random
import string

app = FastAPI(
    title="OTP Service",
    description="Handles one-time password (OTP) generation and verification",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "otp",
            "description": "Endpoints for generating and verifying OTPs"
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

class OTPRequest(BaseModel):
    phone_number: str

class OTPValidateRequest(BaseModel):
    phone_number: str
    otp: str

@app.post("/otp/generate", tags=["otp"], summary="Generate OTP for a phone number")
async def generate_otp(request: OTPRequest):
    otp = ''.join(random.choices(string.digits, k=6))
    redis_client.setex(f"otp:{request.phone_number}", 300, otp)  # 5-minute TTL
    return {"message": "OTP generated", "otp": otp}  # For testing

@app.post("/otp/validate", tags=["otp"], summary="Validate OTP for a phone number")
async def validate_otp(request: OTPValidateRequest):
    stored_otp = redis_client.get(f"otp:{request.phone_number}")
    if not stored_otp or stored_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    redis_client.delete(f"otp:{request.phone_number}")
    return {"message": "OTP validated"}

@app.get("/", tags=["root"], summary="Root Endpoint of OTP Service")
def read_root():
    return {"message": "OTP Service"}