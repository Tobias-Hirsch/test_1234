import os
from datetime import datetime, timedelta
import logging
from ..core.config import settings
from app.services import chat_data_service
from app.modules.minio_module import delete_document_from_minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

async def remove_old_conversations():
    """
    Removes old chat conversations and their associated MinIO files
    if they haven't been updated for a specified number of days.
    """
    try:
        days_str = settings.REMOVE_OLD_CONVERSATIONS_AFTER_DAYS
        if not days_str:
            logger.warning("REMOVE_OLD_CONVERSATIONS_AFTER_DAYS not set in .env. Skipping conversation cleanup.")
            return

        try:
            days_to_keep = int(days_str)
            if days_to_keep <= 0:
                logger.info("REMOVE_OLD_CONVERSATIONS_AFTER_DAYS is set to 0 or less. Skipping conversation cleanup.")
                return
        except ValueError:
            logger.error(f"Invalid value for REMOVE_OLD_CONVERSATIONS_AFTER_DAYS: {days_str}. Must be an integer.")
            return

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        logger.info(f"Starting conversation cleanup. Deleting conversations last updated before: {cutoff_date.isoformat()} UTC")

        all_conversations = await chat_data_service.get_all_conversations() 
        
        if not all_conversations:
            logger.info("No conversations found for cleanup.")
            return

        deleted_count = 0
        for conversation in all_conversations:
            conversation_id = conversation.get('_id')
            updated_at = conversation.get('updated_at')

            if not updated_at or updated_at < cutoff_date:
                logger.info(f"Conversation {conversation_id} (Title: {conversation.get('title', 'N/A')}) is old ({updated_at}) and will be deleted.")
                
                # Delete associated MinIO files
                if 'messages' in conversation:
                    for message in conversation['messages']:
                        if 'attachments' in message:
                            for attachment in message['attachments']:
                                object_name = attachment.get('object_name')
                                bucket_name = attachment.get('bucket_name')
                                if object_name and bucket_name:
                                    try:
                                        delete_document_from_minio(object_name, bucket_name)
                                        logger.info(f"Deleted MinIO object: {object_name} from bucket: {bucket_name}")
                                    except S3Error as e:
                                        logger.error(f"MinIO S3Error deleting {object_name} from {bucket_name}: {e}")
                                    except Exception as e:
                                        logger.error(f"Error deleting MinIO object {object_name} from {bucket_name}: {e}")
                                else:
                                    logger.warning(f"Attachment in conversation {conversation_id} missing object_name or bucket_name: {attachment}")

                # Delete conversation from database
                success = await chat_data_service.delete_conversation(conversation_id)
                if success:
                    deleted_count += 1
                    logger.info(f"Successfully deleted conversation {conversation_id} from database.")
                else:
                    logger.error(f"Failed to delete conversation {conversation_id} from database.")
            else:
                logger.info(f"Conversation {conversation_id} (Title: {conversation.get('title', 'N/A')}) is recent ({updated_at}). Skipping.")

        logger.info(f"Conversation cleanup finished. Total conversations deleted: {deleted_count}")

    except Exception as e:
        logger.error(f"An unexpected error occurred during conversation cleanup: {e}", exc_info=True)