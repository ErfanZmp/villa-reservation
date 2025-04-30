from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .redis_client import redis_client
import random
import string

app = FastAPI()

class OTPRequest(BaseModel):
    phone_number: str

class OTPValidateRequest(BaseModel):
    phone_number: str
    otp: str

@app.post("/otp/generate")
async def generate_otp(request: OTPRequest):
    otp = ''.join(random.choices(string.digits, k=6))
    redis_client.setex(f"otp:{request.phone_number}", 300, otp)  # 5-minute TTL
    # In production, integrate with an SMS gateway
    return {"message": "OTP generated", "otp": otp}  # For testing

@app.post("/otp/validate")
async def validate_otp(request: OTPValidateRequest):
    stored_otp = redis_client.get(f"otp:{request.phone_number}")
    if not stored_otp or stored_otp.decode() != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    redis_client.delete(f"otp:{request.phone_number}")
    return {"message": "OTP validated"}