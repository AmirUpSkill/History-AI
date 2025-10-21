from typing import List, Optional
from uuid import UUID
from fastapi import (
    APIRouter, Depends, HTTPException, status,
    Form, UploadFile, File
)
from sqlalchemy.orm import Session

from app.schemas.card import CardResponse
from app.services.card_service import (
    CardService, CardNotFoundError, AIGenerationError, PDFParsingError
)
from app.dependencies import get_db, get_card_service

router = APIRouter()

# --- API To Get the List of Cards ---
@router.get(
    "/",
    response_model=List[CardResponse],
    summary="List and Search for Cards"
)
def list_cards(
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """
    Retrieves a list of all historical event cards, with an option to filter by title.
    """
    cards = card_service.get_cards(db, title_filter=title)
    return cards

# --- API To Generate The Card --- 
@router.post(
    "/",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a New AI Card"
)
async def create_card(
    title: str = Form(...),
    system_prompt: str = Form(...),
    topics_to_cover: str = Form(...),
    context_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """
    Creates a new historical event card using AI.
    Accepts form data, including an optional PDF file for context.
    """
    pdf_bytes = await context_file.read() if context_file else None
    
    try:
        new_card = card_service.create_card_from_ai(
            db=db,
            title=title,
            system_prompt=system_prompt,
            topcis_to_cover=topics_to_cover, 
            pdf_bytes=pdf_bytes
        )
        return new_card
    except (AIGenerationError, PDFParsingError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

# --- API Endpoint to Get A Specific Card --- 
@router.get(
    "/{card_id}",
    response_model=CardResponse,
    summary="Get Card Details"
)
def get_card_details(
    card_id: UUID,
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """
    Retrieves the full details of a single historical event card by its unique ID.
    """
    try:
        card = card_service.get_card(db, card_id=card_id)
        return card
    except CardNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )