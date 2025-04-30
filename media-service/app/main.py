from fastapi import FastAPI, File, UploadFile, HTTPException
from .minio_client import minio_client
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
app = FastAPI()

@app.post("/media/upload", tags=["media"])
async def upload_image(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        minio_client.put_object(
            bucket_name="villa-images",
            object_name=f"{file_id}_{file.filename}",
            data=file.file,
            length=-1,
            content_type=file.content_type,
            part_size=10*1024*1024
        )
        url = f"http://{os.getenv('MINIO_HOST')}/villa-images/{file_id}_{file.filename}"
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/media/{image_id}", tags=["media"])
async def get_image(image_id: str):
    try:
        response = minio_client.get_object("villa-images", image_id)
        return {"data": response.read()}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")
    
@app.get("/", tags=["root"], summary="Root Endpoint of the Media Service")
async def read_root():
    return {"message": "Media Service is running"}