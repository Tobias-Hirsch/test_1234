from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Optional

from app import models, schemas
from app.models.database import get_db

class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_feedback(
        self,
        *,
        message_id: str,
        user_id: int,
        feedback_in: schemas.FeedbackCreate,
    ) -> Optional[models.MessageFeedback]:
        """
        Creates, updates, or deletes a feedback entry for a message.
        - If rating is provided, it creates or updates the feedback.
        - If rating is null, it deletes the existing feedback.
        """
        db_feedback = self.db.query(models.MessageFeedback).filter(
            models.MessageFeedback.message_id == message_id,
            models.MessageFeedback.user_id == user_id
        ).first()

        if db_feedback:
            if feedback_in.rating is not None:
                # Update existing feedback
                db_feedback.rating = feedback_in.rating
            else:
                # Delete existing feedback if rating is null
                self.db.delete(db_feedback)
                self.db.commit()
                return None
        elif feedback_in.rating is not None:
            # Create new feedback only if rating is not null
            db_feedback = models.MessageFeedback(
                message_id=message_id,
                user_id=user_id,
                rating=feedback_in.rating,
            )
            self.db.add(db_feedback)
        else:
            # No existing feedback and new rating is null, do nothing
            return None

        self.db.commit()
        if db_feedback:
            self.db.refresh(db_feedback)
        return db_feedback

def get_feedback_service(db: Session = Depends(get_db)) -> FeedbackService:
    return FeedbackService(db)