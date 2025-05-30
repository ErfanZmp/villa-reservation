from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import Reservation
from ..dependencies import get_db, get_current_user
from datetime import date
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
VILLA_SERVICE_URL = os.getenv("VILLA_SERVICE_URL")
router = APIRouter()

class ReservationCreate(BaseModel):
    villa_id: int
    check_in_date: date
    check_out_date: date
    people_count: int

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    villa_id: int
    check_in_date: date
    check_out_date: date
    people_count: int
    total_price: float

    class Config:
        orm_mode = True

class ReservationDateRange(BaseModel):
    check_in_date: date
    check_out_date: date

@router.post("/", response_model=ReservationResponse)
async def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Validate dates
    if reservation.check_in_date >= reservation.check_out_date:
        raise HTTPException(status_code=400, detail="Invalid dates: check-in must be before check-out")

    # Check villa exists
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{VILLA_SERVICE_URL}/villas/{reservation.villa_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Villa not found")
            villa = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch villa details")

    # Validate people count
    if reservation.people_count > villa["maximum_capacity"]:
        raise HTTPException(status_code=400, detail="People count exceeds maximum capacity")

    # Check for overlapping reservations
    overlapping = db.query(Reservation).filter(
        Reservation.villa_id == reservation.villa_id,
        Reservation.check_in_date < reservation.check_out_date,
        Reservation.check_out_date > reservation.check_in_date
    ).first()
    if overlapping:
        raise HTTPException(
            status_code=400,
            detail=f"Reservation dates overlap with an existing reservation"
        )

    # Calculate total price
    days = (reservation.check_out_date - reservation.check_in_date).days
    extra_people = max(0, reservation.people_count - villa["base_capacity"])
    total_price = (villa["base_price_per_night"] * days) + (extra_people * villa["extra_person_price"] * days)

    # Create reservation
    db_reservation = Reservation(
        user_id=user["id"],
        villa_id=reservation.villa_id,
        check_in_date=reservation.check_in_date,
        check_out_date=reservation.check_out_date,
        people_count=reservation.people_count,
        total_price=total_price
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.get("/", response_model=list[ReservationResponse])
async def list_reservations(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    reservations = db.query(Reservation).filter(Reservation.user_id == user["id"]).all()
    return reservations

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(reservation_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.user_id == user["id"]
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.get("/villa/{villa_id}/dates", response_model=list[ReservationDateRange])
async def get_villa_reservation_dates(villa_id: int, db: Session = Depends(get_db)):
    
    # Verify villa exists
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{VILLA_SERVICE_URL}/villas/{villa_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Villa not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch villa details")

    # Get all reservations for the villa
    reservations = db.query(Reservation).filter(Reservation.villa_id == villa_id).all()
    date_ranges = [
        ReservationDateRange(
            check_in_date=reservation.check_in_date,
            check_out_date=reservation.check_out_date
        ) for reservation in reservations
    ]
    return date_ranges
