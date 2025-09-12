# backend/app/services/chat_lifecycle_service.py
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException

from app.models.database import User
from app.services import chat_data_service
from app.services.conversation_service import ConversationService
from app.schemas import chat_schemas
from app.services.chat_attachment_service import ChatAttachmentService

logger = logging.getLogger(__name__)

class ChatLifecycleService:
    def __init__(
        self,
        conversation_service: ConversationService,
        attachment_service: ChatAttachmentService,
    ):
        self.conversation_service = conversation_service
        self.attachment_service = attachment_service

    async def _get_conversation_state_or_load_from_db(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        Gets conversation state from Redis. If not found, loads from MongoDB,
        caches it in Redis, and returns it. Also ensures user ownership.
        """
        user_id_int = int(user_id)
        conversation_state = self.conversation_service.get_conversation_state(user_id_int, conversation_id)

        if not conversation_state:
            conversation_from_db = await chat_data_service.get_conversation_by_id(conversation_id)
            if not conversation_from_db:
                raise HTTPException(status_code=404, detail="Conversation not found")
            if conversation_from_db['user_id'] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

            # Initialize conversation state from DB data and cache in Redis
            conversation_state = {
                "history": conversation_from_db.get("messages", []),
                "context": {},
                "variables": {},
                "attached_files": [] # Note: This might not be perfectly in sync if not managed carefully
            }
            self.conversation_service.save_conversation_state(user_id_int, conversation_id, conversation_state)
            logger.info(f"Conversation {conversation_id} loaded from DB and cached in Redis.")
        
        return conversation_state

    def _format_timestamps_and_urls(self, conv: Dict[str, Any]):
        """Helper to format datetime objects and add download URLs."""
        if 'created_at' in conv and isinstance(conv['created_at'], datetime):
            conv['created_at'] = conv['created_at'].isoformat()
        if 'updated_at' in conv and isinstance(conv['updated_at'], datetime):
            conv['updated_at'] = conv['updated_at'].isoformat()
        
        if 'messages' in conv:
            conversation_id = conv.get('_id')
            for msg in conv['messages']:
                if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
                if 'attachments' in msg:
                    for att in msg['attachments']:
                        if 'upload_timestamp' in att and isinstance(att['upload_timestamp'], datetime):
                            att['upload_timestamp'] = att['upload_timestamp'].isoformat()
                        
                        att_id = att.get('id') or att.get('_id')
                        msg_id = msg.get('_id')
                        if att_id and msg_id and conversation_id:
                            att['download_url'] = f"/chat/conversations/{conversation_id}/messages/{msg_id}/attachments/{att_id}/download/"
        return conv

    async def get_all_user_conversations(self, current_user: User) -> List[Dict[str, Any]]:
        """Gets all conversations for a user, hydrating with Redis data if available."""
        user_id_str = str(current_user.id)
        user_id_int = current_user.id
        
        conversations_from_db = await chat_data_service.get_conversations_by_user(user_id_str)

        for conv in conversations_from_db:
            conversation_id = conv['_id']
            redis_state = self.conversation_service.get_conversation_state(user_id_int, conversation_id)
            
            if redis_state and 'history' in redis_state:
                conv['messages'] = redis_state['history']
            
            self._format_timestamps_and_urls(conv)

        return conversations_from_db

    async def create_conversation(self, title: str, current_user: User) -> Dict[str, Any]:
        """Creates a new conversation and initializes its state in Redis."""
        user_id_str = str(current_user.id)
        user_id_int = current_user.id

        conversation = await chat_data_service.create_conversation(user_id_str, title)
        if not conversation:
            raise HTTPException(status_code=500, detail="Failed to create conversation")

        initial_state = {
            "history": [], "context": {}, "variables": {}, "attached_files": []
        }
        self.conversation_service.save_conversation_state(user_id_int, str(conversation['_id']), initial_state)
        logger.info(f"Initial conversation state for {conversation['_id']} saved to Redis.")

        conversation['messages'] = []
        return self._format_timestamps_and_urls(conversation)

    async def get_messages(self, conversation_id: str, current_user: User) -> List[Dict[str, Any]]:
        """Gets messages for a specific conversation."""
        conversation_state = await self._get_conversation_state_or_load_from_db(str(current_user.id), conversation_id)
        messages_data = conversation_state.get("history", [])
        
        # Create a temporary conversation dict to reuse the formatting function
        temp_conv_for_formatting = {'_id': conversation_id, 'messages': messages_data}
        formatted_conv = self._format_timestamps_and_urls(temp_conv_for_formatting)
        
        return formatted_conv['messages']

    async def find_message_and_attachment(self, conversation_id: str, message_id: str, attachment_id: str, current_user: User) -> Tuple[Dict, Dict]:
        """Finds a specific message and attachment in a conversation."""
        conversation_state = await self._get_conversation_state_or_load_from_db(str(current_user.id), conversation_id)
        
        message = next((msg for msg in conversation_state.get('history', []) if str(msg.get('_id')) == message_id), None)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found in conversation history")

        attachment = next((att for att in message.get('attachments', []) if str(att.get('id') or att.get('_id')) == attachment_id), None)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found in message")
            
        return message, attachment

    async def delete_attachment(self, conversation_id: str, message_id: str, attachment_id: str, current_user: User) -> Dict[str, Any]:
        """Deletes an attachment from a message, including from MinIO."""
        user_id_str = str(current_user.id)
        user_id_int = current_user.id

        _, attachment_to_delete = await self.find_message_and_attachment(conversation_id, message_id, attachment_id, current_user)
        
        # Delete from MinIO
        self.attachment_service.handle_delete(attachment_to_delete)

        # Remove metadata from Redis
        conversation_state = self.conversation_service.get_conversation_state(user_id_int, conversation_id)
        if conversation_state:
            message_found = False
            for msg in conversation_state['history']:
                if str(msg.get('_id')) == message_id:
                    message_found = True
                    if 'attachments' in msg:
                        msg['attachments'] = [att for att in msg['attachments'] if str(att.get('id') or att.get('_id')) != attachment_id]
                    break
            
            if message_found:
                conversation_state['attached_files'] = [
                    att for att in conversation_state.get('attached_files', [])
                    if str(att.get('id')) != attachment_id
                ]
                self.conversation_service.save_conversation_state(user_id_int, conversation_id, conversation_state)
                logger.info(f"Attachment {attachment_id} metadata removed from Redis for conversation {conversation_id}.")
        
        return conversation_state

    async def delete_conversation(self, conversation_id: str, current_user: User):
        """Deletes a full conversation and all its associated data."""
        user_id_str = str(current_user.id)
        user_id_int = current_user.id

        # Verify ownership from DB first
        conversation_db = await chat_data_service.get_conversation_by_id(conversation_id)
        if not conversation_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation_db['user_id'] != user_id_str:
            raise HTTPException(status_code=403, detail="Not authorized to delete this conversation")

        # Delete all associated attachments from MinIO using Redis state as source of truth
        conversation_state = self.conversation_service.get_conversation_state(user_id_int, conversation_id)
        if conversation_state:
            all_attachments = conversation_state.get('attached_files', [])
            processed_object_names = set()
            for attachment in all_attachments:
                object_name = attachment.get('object_name')
                if object_name and object_name not in processed_object_names:
                    self.attachment_service.handle_delete(attachment)
                    processed_object_names.add(object_name)

        # Delete from Redis
        self.conversation_service.delete_conversation_state(user_id_int, conversation_id)
        logger.info(f"Conversation state for {conversation_id} deleted from Redis.")

        # Delete from MongoDB
        success = await chat_data_service.delete_conversation(conversation_id)
        if not success:
            # This is a problem, as state is now inconsistent.
            logger.error(f"Failed to delete conversation {conversation_id} from database after deleting from cache and storage.")
            raise HTTPException(status_code=500, detail="Failed to delete conversation from database. State may be inconsistent.")

    async def update_title(self, conversation_id: str, new_title: str, current_user: User) -> Dict[str, Any]:
        """Updates the title of a conversation."""
        user_id_str = str(current_user.id)
        
        # Verify ownership
        conversation = await chat_data_service.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation['user_id'] != user_id_str:
            raise HTTPException(status_code=403, detail="Not authorized to modify this conversation")

        success = await chat_data_service.update_conversation_title(conversation_id, new_title)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update conversation title")

        updated_conversation = await chat_data_service.get_conversation_by_id(conversation_id)
        return self._format_timestamps_and_urls(updated_conversation)