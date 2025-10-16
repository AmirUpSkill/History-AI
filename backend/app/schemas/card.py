from uuid import UUID 
from typing import List 
from pydantic import BaseModel, Field, ConfigDict

# --- Create Base Card Schema --- 
class CardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    keywords: List[str] = Field(default=..., min_length=1)
# --- Create Card Creation Input Schema --- 
class CardCreateInput(BaseModel):
    """
        Card Creation Input Schema . 
    """
    title: str = Field(...,min_length=1,max_length=200)
    system_promt: str = Field(...,min_length=10)
    topcis_to_cover: str = Field(...,min_length=5)
    context_text: str | None = None 
# --- Create Card Response Schema --- 
class CardResponse(CardBase):
    """
        Card Response Schema . 
    """
    id: UUID 
    model_config = ConfigDict(from_attributes=True)
