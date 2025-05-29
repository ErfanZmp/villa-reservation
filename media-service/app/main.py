from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .minio_client import minio_client
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

# Supported image formats and their extensions
IMAGE_FORMATS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp"
}

app = FastAPI(
    title="Media Service",
    description="Handles image uploads and retrieval for villas",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "media",
            "description": "Endpoints for uploading and retrieving images"
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

@app.post("/media/upload", tags=["media"])
async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate content type
        if file.content_type not in IMAGE_FORMATS:
            raise HTTPException(status_code=400, detail="Unsupported image format. Supported formats: PNG, JPEG, GIF, WebP")

        # Generate object name using UUID and content-type-based extension
        file_id = str(uuid.uuid4())
        file_extension = IMAGE_FORMATS[file.content_type]
        object_name = f"{file_id}{file_extension}"

        # Upload to MinIO
        minio_client.put_object(
            bucket_name="villa-images",
            object_name=object_name,
            data=file.file,
            length=-1,
            content_type=file.content_type,
            part_size=10*1024*1024
        )

        # Generate media-service URL
        media_service_host = os.getenv("MEDIA_SERVICE_HOST", "localhost:8004")
        url = f"http://{media_service_host}/media/{object_name}"
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stream_minio_object(bucket_name: str, object_name: str):
    response = None
    try:
        response = minio_client.get_object(bucket_name, object_name)
        while True:
            chunk = response.read(8192)  # Read in 8KB chunks
            if not chunk:
                break
            yield chunk
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")
    finally:
        if response:
            response.close()
            response.release_conn()

@app.get("/media/{image_id}", tags=["media"])
async def get_image(image_id: str):
    try:
        # Check if object exists
        minio_client.stat_object("villa-images", image_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")
    
    content_type = "image/png"  # Default
    try:
        # Get object metadata to determine Content-Type
        obj_info = minio_client.stat_object("villa-images", image_id)
        content_type = obj_info.content_type or "image/png"
    except Exception:
        print(f"Could not get metadata for {image_id}, using default Content-Type")
    
    return StreamingResponse(
        content=stream_minio_object("villa-images", image_id),
        media_type=content_type,
        headers={
            "Content-Disposition": f"inline; filename=\"{image_id}\"",
            "Cache-Control": "public, max-age=3600"  # Allow caching for 1 hour
        }
    )
