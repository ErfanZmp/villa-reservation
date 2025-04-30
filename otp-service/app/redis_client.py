import redis
from dotenv import load_dotenv
import os

load_dotenv()
redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, decode_responses=True)