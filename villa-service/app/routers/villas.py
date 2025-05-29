from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import json
from dotenv import load_dotenv
import os

from ..models import Villa
from ..dependencies import get_db, get_current_admin

load_dotenv()
MEDIA_SERVICE_URL = os.getenv("MEDIA_SERVICE_URL")
router = APIRouter()

class VillaCreate(BaseModel):
    title: str
    city: str
    address: str
    base_capacity: int
    maximum_capacity: int
    area: float
    bed_count: int
    has_pool: bool
    has_cooling_system: bool
    base_price_per_night: float
    extra_person_price: float
    rating: float

class VillaResponse(BaseModel):
    id: int
    title: str
    images: str
    city: str
    address: str
    base_capacity: int
    maximum_capacity: int
    area: float
    bed_count: int
    has_pool: bool
    has_cooling_system: bool
    base_price_per_night: float
    extra_person_price: float
    rating: float

@router.post("/", response_model=VillaResponse)
async def create_villa(
    villa: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        villa_data = json.loads(villa)
        villa_obj = VillaCreate(**villa_data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail="Invalid JSON format for villa")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Villa validation error: {str(e)}")

    # Upload image to media-service
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (image.filename, await image.read(), image.content_type)}
            response = await client.post(f"{MEDIA_SERVICE_URL}/media/upload", files=files)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to upload image")
            image_url = response.json().get("url")
            if not image_url:
                raise HTTPException(status_code=500, detail="No image URL returned from media-service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload error: {str(e)}")

    # Create villa in database
    db_villa = Villa(**villa_obj.model_dump(), images=image_url)
    db.add(db_villa)
    db.commit()
    db.refresh(db_villa)
    return db_villa

@router.put("/{villa_id}", response_model=VillaResponse)
async def update_villa(
    villa_id: int,
    villa: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    db_villa = db.query(Villa).filter(Villa.id == villa_id).first()
    if not db_villa:
        raise HTTPException(status_code=404, detail="Villa not found")

    # Parse and validate villa data
    try:
        villa_data = json.loads(villa)
        villa_obj = VillaCreate(**villa_data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail="Invalid JSON format for villa")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Villa validation error: {str(e)}")

    # Handle image upload if provided
    image_url = db_villa.images
    if image:
        try:
            async with httpx.AsyncClient() as client:
                files = {"file": (image.filename, await image.read(), image.content_type)}
                response = await client.post(f"{MEDIA_SERVICE_URL}/media/upload", files=files)
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="Failed to upload image")
                image_url = response.json().get("url")
                if not image_url:
                    raise HTTPException(status_code=500, detail="No image URL returned from media-service")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload error: {str(e)}")

    # Update villa attributes
    for key, value in villa_obj.model_dump().items():
        setattr(db_villa, key, value)
    db_villa.images = image_url
    db.commit()
    db.refresh(db_villa)
    return db_villa

@router.delete("/{villa_id}")
async def delete_villa(villa_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    db_villa = db.query(Villa).filter(Villa.id == villa_id).first()
    if not db_villa:
        raise HTTPException(status_code=404, detail="Villa not found")
    db.delete(db_villa)
    db.commit()
    return {"message": "Villa deleted"}

@router.get("/", response_model=List[VillaResponse])
async def list_villas(city: str = None, min_capacity: int = None, max_price: float = None, db: Session = Depends(get_db)):
    query = db.query(Villa)
    if city:
        query = query.filter(Villa.city == city)
    if min_capacity:
        query = query.filter(Villa.maximum_capacity >= min_capacity)
    if max_price:
        query = query.filter(Villa.base_price_per_night <= max_price)
    return query.all()

@router.get("/{villa_id}", response_model=VillaResponse)
async def get_villa(villa_id: int, db: Session = Depends(get_db)):
    villa = db.query(Villa).filter(Villa.id == villa_id).first()
    if not villa:
        raise HTTPException(status_code=404, detail="Villa not found")
    return villa