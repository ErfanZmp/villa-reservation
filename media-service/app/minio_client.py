from minio import Minio
from dotenv import load_dotenv
import os

load_dotenv()
minio_client = Minio(
    os.getenv("MINIO_HOST"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Create bucket if it doesn't exist
if not minio_client.bucket_exists("villa-images"):
    minio_client.make_bucket("villa-images")