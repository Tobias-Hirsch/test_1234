from pydantic import BaseModel
from typing import Literal, Optional

class FeedbackBase(BaseModel):
    rating: Optional[Literal['like', 'dislike']] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    message_id: str
    user_id: int

    class Config:
        orm_mode = True