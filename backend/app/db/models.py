import uuid 
from sqlalchemy import Column , String , Text 
from sqlalchemy.dialects.postgresql import UUID,ARRAY 
# --- Import the Parent Class --- 
from .base import Base
# --- Card Model --- 
class Card(Base):
    """
        Represent A Historical Even Card in the DB . 
    """
    __tablename__ = "cards"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    keywords = Column(ARRAY(String), nullable=False)
