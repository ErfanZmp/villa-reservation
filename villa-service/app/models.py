from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Villa(Base):
    __tablename__ = "villas"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    images = Column(String)  # Comma-separated URLs
    city = Column(String, nullable=False)
    address = Column(String, nullable=False)
    base_capacity = Column(Integer, nullable=False)
    maximum_capacity = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)
    bed_count = Column(Integer, nullable=False)
    has_pool = Column(Boolean, default=False)
    has_cooling_system = Column(Boolean, default=False)
    base_price_per_night = Column(Float, nullable=False)
    extra_person_price = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)