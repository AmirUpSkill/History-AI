from typing import Generator 
from app.db.session import SessionLocal 

# --- Get Db ---
def get_db() -> Generator:
    """
        Get a DB Session . 
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
