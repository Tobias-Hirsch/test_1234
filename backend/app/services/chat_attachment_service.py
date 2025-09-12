# backend/app/services/chat_attachment_service.py
import os
import uuid
import shutil
import logging
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from minio.error import S3Error
from datetime import datetime
import aiofiles

from app.schemas import chat_schemas
from app.modules.minio_module import store_document_in_minio, get_document_from_minio, delete_document_from_minio
from app.services.conversation_service import ConversationService
from app.core.config import settings

logger = logging.getLogger(__name__)
chat_attachments_bucket = settings.MINIO_CHAT_BUCKET_NAME

class ChatAttachmentService:
    def __init__(self, conversation_service: ConversationService):
        self.conversation_service = conversation_service

    async def handle_upload(
        self,
        files: List[UploadFile],
        current_user_id: str,
        conversation_id: Optional[str] = None,
    ) -> List[chat_schemas.Attachment]:
        """Handles file uploads, stores them in MinIO, and updates conversation state."""
        temp_upload_dir = "temp_chat_uploads"
        os.makedirs(temp_upload_dir, exist_ok=True)

        uploaded_files_info: List[chat_schemas.Attachment] = []
        total_uploaded_size = 0
        max_total_size = 100 * 1024 * 1024  # 100MB limit

        for file in files:
            if total_uploaded_size + file.size > max_total_size:
                logger.warning(f"File {file.filename} exceeds total size limit. Skipping.")
                await file.close()
                continue

            upload_session_dir = os.path.join(temp_upload_dir, str(uuid.uuid4()))
            os.makedirs(upload_session_dir, exist_ok=True)
            temp_file_path = None

            try:
                filename = os.path.basename(file.filename)
                temp_file_path = os.path.join(upload_session_dir, filename)

                async with aiofiles.open(temp_file_path, 'wb') as out_file:
                    while content := await file.read(1024):
                        await out_file.write(content)

                object_name = f"{current_user_id}/{uuid.uuid4()}/{filename}"
                store_document_in_minio(temp_file_path, object_name, chat_attachments_bucket)

                attachment_id = str(uuid.uuid4())
                uploaded_files_info.append(chat_schemas.Attachment(
                    id=attachment_id,
                    filename=filename,
                    bucket_name=chat_attachments_bucket,
                    object_name=object_name,
                    size=file.size,
                    content_type=file.content_type,
                    upload_timestamp=datetime.now()
                ))
                total_uploaded_size += file.size
            except S3Error as e:
                logger.error(f"MinIO error uploading file {file.filename}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
            finally:
                await file.close()
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if os.path.exists(upload_session_dir):
                    try:
                        shutil.rmtree(upload_session_dir)
                    except Exception as e:
                        logger.error(f"Error cleaning up upload directory {upload_session_dir}: {e}")

        if not uploaded_files_info:
            raise HTTPException(status_code=400, detail="No files were uploaded successfully.")

        if conversation_id:
            self._add_attachments_to_conversation_state(current_user_id, conversation_id, uploaded_files_info)

        return uploaded_files_info

    def _add_attachments_to_conversation_state(
        self,
        user_id: str,
        conversation_id: str,
        attachments: List[chat_schemas.Attachment]
    ):
        """Adds attachment metadata to the conversation state in Redis."""
        conversation_state = self.conversation_service.get_conversation_state(int(user_id), conversation_id)
        if conversation_state:
            for att_info in attachments:
                conversation_state["attached_files"].append(att_info.model_dump())
            self.conversation_service.save_conversation_state(int(user_id), conversation_id, conversation_state)
            logger.info(f"Attached files updated in Redis for conversation {conversation_id}.")
        else:
            logger.warning(f"Conversation {conversation_id} not found in Redis for updating attached files.")

    async def handle_download(self, attachment: dict):
        """Streams an attachment file from MinIO for download."""
        temp_download_dir = "temp_chat_downloads"
        os.makedirs(temp_download_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_download_dir, attachment['filename'])

        try:
            get_document_from_minio(attachment['object_name'], attachment['bucket_name'], temp_file_path)

            async def file_iterator():
                try:
                    async with aiofiles.open(temp_file_path, 'rb') as f:
                        while chunk := await f.read(1024):
                            yield chunk
                finally:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    # Clean up directory if empty
                    if os.path.exists(temp_download_dir) and not os.listdir(temp_download_dir):
                        try:
                            shutil.rmtree(temp_download_dir)
                        except Exception as e:
                            logger.error(f"Error cleaning up empty download directory {temp_download_dir}: {e}")
            
            return file_iterator()
        except S3Error as e:
            logger.error(f"MinIO Error downloading file {attachment['object_name']}: {e}")
            raise HTTPException(status_code=500, detail="Failed to download attachment from storage")
        except FileNotFoundError:
            logger.error(f"Temporary file not found after download attempt: {temp_file_path}")
            raise HTTPException(status_code=500, detail="Temporary file not found after download attempt")
        except Exception as e:
            logger.error(f"Error preparing attachment for download {attachment.get('id')}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to download attachment")

    def handle_delete(self, attachment: dict):
        """Deletes an attachment from MinIO."""
        try:
            delete_document_from_minio(attachment['object_name'], attachment['bucket_name'])
            logger.info(f"Deleted attachment object '{attachment['object_name']}' from MinIO bucket '{attachment['bucket_name']}'.")
        except S3Error as e:
            logger.warning(f"MinIO Error deleting file {attachment['object_name']}: {e}. Continuing with metadata removal.")
            # We pass here to allow metadata to be removed even if MinIO deletion fails
            pass