from typing import Generator
from app.db.session import SessionLocal
from app.core.config import settings
from app.services.ai_service import AIService
from app.services.card_service import CardService

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
# --- AI Service Dependency --- 
def get_ai_service() -> AIService:
    """
        Dependency to create and get an instance of the AIService .
    """
    return AIService(api_key=settings.GEMINI_API_KEY)
# --- Card Service Dependency --- 
def get_card_service() -> CardService:
    """
        Dependency that creates an AIService and inject it .
    """
    ai_service = get_ai_service()
    return CardService(ai_service = ai_service)