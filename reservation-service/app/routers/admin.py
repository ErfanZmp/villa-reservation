from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import Reservation
from ..dependencies import get_db, get_current_admin
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()
VILLA_SERVICE_URL = os.getenv("VILLA_SERVICE_URL")
router = APIRouter()

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

@router.get("/all", response_model=list[ReservationResponse])
async def list_all_reservations(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    reservations = db.query(Reservation).all()
    return reservations

@router.get("/user/{user_id}", response_model=list[ReservationResponse])
async def list_user_reservations(user_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    reservations = db.query(Reservation).filter(Reservation.user_id == user_id).all()
    if not reservations:
        raise HTTPException(status_code=404, detail="No reservations found for this user")
    return reservations

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(reservation)
    db.commit()
    return  {"detail": "Reservation deleted successfully"}