from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from app.core.config import settings 

# --- Create The SQLAlchemy engine --- 
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
# --- Create a configured "Session" class ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
