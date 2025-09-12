# backend/app/routers/chat.py
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services import auth
from app import schemas, models
from app.models import User
from app.services.auth import get_redis_client # Import get_redis_client
from app.services.conversation_service import ConversationService, get_conversation_service
from app.services.chat_attachment_service import ChatAttachmentService
from app.services.chat_lifecycle_service import ChatLifecycleService
from app.services.chat_response_service import ChatResponseService
from app.services.feedback_service import FeedbackService, get_feedback_service
from app.utils.stream_processors import sse_stream_formatter

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Dependency Injection for New Services ---

def get_chat_attachment_service(
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> ChatAttachmentService:
    return ChatAttachmentService(conversation_service)

def get_chat_lifecycle_service(
    conversation_service: ConversationService = Depends(get_conversation_service),
    attachment_service: ChatAttachmentService = Depends(get_chat_attachment_service)
) -> ChatLifecycleService:
    return ChatLifecycleService(conversation_service, attachment_service)

def get_chat_response_service(
    db: Session = Depends(get_db),
    redis_client: Session = Depends(get_redis_client), # Add redis_client dependency
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> ChatResponseService:
    return ChatResponseService(db, redis_client, conversation_service)

# --- Router Endpoints ---

@router.post("/upload_files")
async def upload_chat_files(
    files: List[UploadFile] = File(...),
    conversation_id: Optional[str] = None,
    current_user: User = Depends(auth.get_current_active_user),
    attachment_service: ChatAttachmentService = Depends(get_chat_attachment_service)
):
    """Receives files from the chat, uploads them, and updates conversation state."""
    uploaded_files = await attachment_service.handle_upload(files, str(current_user.id), conversation_id)
    
    return JSONResponse(content={"message": "Files uploaded successfully", "uploaded_files": [
        {
            **att.model_dump(by_alias=True),
            "upload_timestamp": att.upload_timestamp.isoformat() if att.upload_timestamp else None,
            "download_url": "" # Placeholder, can be constructed on frontend if needed
        }
        for att in uploaded_files
    ]})

@router.get("/conversations", response_model=List[schemas.Conversation], include_in_schema=False)
@router.get("/conversations/", response_model=List[schemas.Conversation])
async def get_user_conversations(
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service)
) -> List[schemas.Conversation]:
    """Gets all chat conversations for the current user."""
    conversations = await lifecycle_service.get_all_user_conversations(current_user)
    return conversations

@router.post("/conversations", response_model=schemas.Conversation, include_in_schema=False)
@router.post("/conversations/", response_model=schemas.Conversation)
async def create_user_conversation(
    conversation_create: schemas.ConversationCreate,
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service)
) -> schemas.Conversation:
    """Creates a new chat conversation."""
    conversation = await lifecycle_service.create_conversation(conversation_create.title, current_user)
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=List[schemas.ChatMessage], include_in_schema=False)
@router.get("/conversations/{conversation_id}/messages/", response_model=List[schemas.ChatMessage])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service)
) -> List[schemas.ChatMessage]:
    """Gets messages for a specific conversation."""
    messages = await lifecycle_service.get_messages(conversation_id, current_user)
    return messages

@router.post("/conversations/{conversation_id}/messages", response_model=None, include_in_schema=False)
@router.post("/conversations/{conversation_id}/messages/", response_model=None)
async def add_conversation_message(
    conversation_id: str,
    message_create: schemas.MessageCreate,
    current_user: User = Depends(auth.get_current_active_user),
    response_service: ChatResponseService = Depends(get_chat_response_service)
) -> StreamingResponse | JSONResponse:
    """Adds a message and streams the bot's response."""
    if not (message_create.search_ai_active or message_create.search_rosti_active or message_create.search_online_active or message_create.attachments):
        return JSONResponse(content={"message": "Please provide instructions, select a search option, or attach a file."})

    response_generator = await response_service.generate_response(conversation_id, message_create, current_user)
    return StreamingResponse(sse_stream_formatter(response_generator), media_type="text/event-stream")

@router.get("/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/download")
async def download_conversation_attachment(
    conversation_id: str,
    message_id: str,
    attachment_id: str,
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service),
    attachment_service: ChatAttachmentService = Depends(get_chat_attachment_service)
):
    """Downloads a specific attachment from a message."""
    _, attachment = await lifecycle_service.find_message_and_attachment(conversation_id, message_id, attachment_id, current_user)
    file_iterator = await attachment_service.handle_download(attachment)
    return StreamingResponse(file_iterator, media_type=attachment['content_type'], headers={"Content-Disposition": f"attachment; filename=\"{attachment['filename']}\""})

@router.delete("/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}")
async def delete_conversation_attachment(
    conversation_id: str,
    message_id: str,
    attachment_id: str,
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service)
) -> JSONResponse:
    """Deletes a specific attachment from a message."""
    updated_state = await lifecycle_service.delete_attachment(conversation_id, message_id, attachment_id, current_user)
    return JSONResponse(content=updated_state)

@router.delete("/conversations/{conversation_id}")
async def delete_user_conversation(
    conversation_id: str,
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service)
):
    """Deletes a chat conversation and all its data."""
    await lifecycle_service.delete_conversation(conversation_id, current_user)
    return JSONResponse(content={"message": "Conversation deleted successfully"})

@router.post("/conversations/{conversation_id}/title", response_model=schemas.Conversation)
async def update_conversation_title(
    conversation_id: str,
    title_update: schemas.ConversationTitleUpdate,
    current_user: User = Depends(auth.get_current_active_user),
    lifecycle_service: ChatLifecycleService = Depends(get_chat_lifecycle_service)
) -> schemas.Conversation:
    """Updates the title of a specific chat conversation."""
    updated_conversation = await lifecycle_service.update_title(conversation_id, title_update.title, current_user)
    return updated_conversation

@router.post("/messages/{message_id}/feedback", response_model=Optional[schemas.Feedback])
async def create_message_feedback(
    message_id: str,
    feedback: schemas.FeedbackCreate,
    current_user: User = Depends(auth.get_current_active_user),
    feedback_service: FeedbackService = Depends(get_feedback_service),
) -> Response | Optional[models.MessageFeedback]:
    """
    Creates, updates, or deletes a feedback entry for a specific message.
    Returns the feedback object or a 204 No Content if feedback is removed.
    """
    db_feedback = feedback_service.create_or_update_feedback(
        message_id=message_id,
        user_id=current_user.id,
        feedback_in=feedback,
    )

    if db_feedback is None:
        return Response(status_code=204)
    
    return db_feedback
