from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models import Card
from app.schemas.card import CardBase

class CardCRUD:
    """
        CRUD operations for Card Model .
    """
    @staticmethod
    def get(db: Session, id: UUID) -> Optional[Card]:
        """
            Method to Retrieve a single Card by its UUID . 

            Args: 
                db (Session) : The database session . 
                id (UUID) : The UUID of the Card to retrieve . 
            
            Returns: 
                Optional[Card] : The retrieved Card object if found , None otherwise . 
        """ 
        return db.query(Card).filter(Card.id == id).first()
    @staticmethod
    def get_multi(
        db: Session,
        title: Optional[str] = None,
        skip: int = 0,
        limit: int = 100 
    ) -> List[Card]:
        """
            Retrieve mutiple cards with optional title filtering . 

            Args:
                db (Session) : The database session . 
                title (Optional[str]) : The title to filter cards by . Defaults to None . 
                skip (int) : The number of records to skip . Defaults to 0 . 
                limit (int) : The maximum number of records to return . Defaults to 100 . 
            
            Returns: 
                List[Card] : A list of Card objects that match the filtering criteria . 
        """
        query = db.query(Card)

        # --- Apply Filter based on title ---
        if title:
            query = query.filter(Card.title.ilike(f"%{title}%"))
            
        # --- Apply Pagination ---
        query = query.offset(skip).limit(limit)

        return query.all()
    @staticmethod
    def create(db: Session ,*, card_in: CardBase) -> Card:
        """
            Create a new Card in the database 

            Args:
                db (Session) : The database session . 
                card_in (CardBase) : The CardBase schema containing the data for the new Card . 
            
            Returns: 
                Card : The created Card object . 
        """
        # --- Create a new Card --- 
        db_card = Card(
            title=card_in.title,
            description=card_in.description,
            keywords=card_in.keywords
        )
        # --- Add to Session and Commit --- 
        db.add(db_card)
        db.commit()
        # --- Refresh to get the ID --- 
        db.refresh(db_card)
        return db_card

    