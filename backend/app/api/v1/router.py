from fastapi import APIRouter
from app.api.v1.endpoints import cards, ai

api_router = APIRouter()

# --- Include the cards router with a prefix and tags ---
api_router.include_router(
    cards.router,
    prefix="/cards",
    tags=["Cards"]
)

# --- Include the ai router with a prefix and tags ----
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Utilities"]
)