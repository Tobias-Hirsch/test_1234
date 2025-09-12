import logging
from fastapi import UploadFile
from typing import List, Dict, Any
import os
import io
import asyncio
import base64
import uuid
import fitz  # PyMuPDF
 
from app.utils.document_utils import is_scanned_pdf
from app.utils.table_utils import linearize_html_table_to_markdown
from app.utils.dwg_utils import extract_text_from_dwg
from app.services.mineru_service import mineru_client
from app.services.paddleocr_service import call_paddleocr_service
# Placeholder for the new service client we will create
from app.services.latexocr_service import call_latexocr_service
from pathlib import Path

logger = logging.getLogger(__name__)

# --- ARCHITECTURAL NOTE (2025-07-20) ---
# The following function, `_process_with_paddle`, was part of the original "dual-track"
# architecture where scanned PDFs were routed to a full PP-StructureV3 service.
# This approach was deprecated because the PP-StructureV3 model's high VRAM usage
# caused deployment instability.
# The current architecture centralizes all complex document processing (including
# scanned PDFs) in the `_process_with_mineru` function to maximize the use of
# the dedicated GPU for the MinerU service.
# This code is retained for historical reference.
async def _process_with_paddle(file_bytes: bytes, filename: str) -> str:
    """
    Helper function to process a file with the refactored PP-StructureV3 service.
    This function handles the new markdown and base64 image output format.
    """
    logger.info(f"Processing '{filename}' with PaddleOCR (PP-StructureV3).")
    file_like_object = io.BytesIO(file_bytes)
    upload_file = UploadFile(filename=filename, file=file_like_object)
    
    # The service now returns a dictionary with "markdown" and "images" keys
    paddle_result = await call_paddleocr_service(upload_file)
    
    if not paddle_result or 'markdown' not in paddle_result:
        logger.error(f"PaddleOCR V3 processing failed or returned invalid data for '{filename}'.")
        return ""
        
    # Start with the full markdown text returned by the service
    processed_markdown = paddle_result.get('markdown', '')
    images_dict = paddle_result.get('images', {})

    # If there are images, process them and replace their references in the markdown
    if images_dict:
        logger.info(f"Found {len(images_dict)} images in PaddleOCR output to process with LatexOCR.")
        
        # Create a list of tasks to run concurrently
        tasks = []
        for img_path, b64_data in images_dict.items():
            # The markdown reference looks like ![image_name](image_path)
            # We need to replace this entire block with the LaTeX formula.
            # The image name in the markdown is the stem of the path.
            img_name = Path(img_path).stem
            markdown_ref = f"![{img_name}]({img_path})"
            
            try:
                image_bytes = base64.b64decode(b64_data)
                # Create a coroutine for each image to be processed
                tasks.append(process_single_image_and_replace(markdown_ref, image_bytes))
            except Exception as e:
                logger.error(f"Failed to decode base64 for image {img_path}: {e}")

        # Run all image processing tasks in parallel
        replacements = await asyncio.gather(*tasks)

        # Apply the replacements to the markdown text
        for old, new in replacements:
            if new: # Only replace if a formula was successfully recognized
                processed_markdown = processed_markdown.replace(old, new)
            else: # If recognition fails, remove the image reference
                processed_markdown = processed_markdown.replace(old, "")

    return processed_markdown

async def process_single_image_and_replace(markdown_ref: str, image_bytes: bytes) -> tuple[str, str | None]:
    """
    Processes a single image with LatexOCR and returns the original markdown reference
    and the new LaTeX block to replace it with.
    """
    try:
        latex_code = await call_latexocr_service(image_bytes)
        if latex_code:
            # Return the original reference and the new LaTeX block
            return (markdown_ref, f"\n$${latex_code}$$\n")
        else:
            logger.warning(f"LatexOCR returned no result for image ref: {markdown_ref}")
            return (markdown_ref, None)
    except Exception as e:
        logger.error(f"Failed to process image ref {markdown_ref} with LatexOCR: {e}")
        return (markdown_ref, None)

async def _process_image_with_paddle(file_bytes: bytes, filename: str) -> str:
    """
    Helper function to process a single image file with the lightweight PaddleOCR service.
    """
    logger.info(f"Processing image '{filename}' with lightweight PaddleOCR service.")
    file_like_object = io.BytesIO(file_bytes)
    upload_file = UploadFile(filename=filename, file=file_like_object)
    
    # The lightweight service returns a dictionary with a "text" key.
    paddle_result = await call_paddleocr_service(upload_file)
    
    if not paddle_result or 'text' not in paddle_result:
        logger.error(f"Lightweight PaddleOCR processing failed for '{filename}'.")
        return ""
        
    return paddle_result.get('text', '')

def _process_pdf_with_pymupdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Fast-path processing for PDFs using PyMuPDF.
    Extracts text and checks for the presence of significant images.
    Returns a dictionary containing 'text' and 'has_images'.
    """
    text = ""
    has_images = False
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        for page in pdf_document:
            text += page.get_text()
            # get_images(full=True) returns a list of image metadata
            if page.get_images(full=True):
                has_images = True
        pdf_document.close()
    except Exception as e:
        logger.error(f"PyMuPDF failed to process the PDF file: {e}")
        return {"text": "", "has_images": False}
    
    return {"text": text.strip(), "has_images": has_images}


from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2

async def _process_with_mineru(file_bytes: bytes, filename: str) -> str:
    """Helper function to process a file with MinerU."""
    logger.info(f"Processing '{filename}' with MinerU.")

    # CRITICAL FIX: Pre-process PDF bytes using the same function as the official test script.
    # This step standardizes the PDF bytes and is likely essential for the VLM model.
    if filename.lower().endswith('.pdf'):
        logger.info(f"Applying PyPDFium2 standardization to '{filename}'.")
        try:
            file_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(file_bytes)
        except Exception as e:
            logger.error(f"PyPDFium2 preprocessing failed for '{filename}': {e}")
            return ""

    mineru_result = await mineru_client.process_document_bytes(file_bytes, filename)
    
    if not mineru_result or 'result' not in mineru_result:
        logger.error(f"MinerU processing failed or returned invalid data for '{filename}'.")
        return ""
        
    pdf_info = mineru_result.get('result', {})
    content_parts = []
    
    # The pdf_info structure contains pages, and each page contains blocks.
    # DEFENSIVE FIX: The structure returned by MinerU can vary. Sometimes pdf_info is
    # a dictionary containing 'pages', and sometimes it's the list of pages directly.
    pages = []
    if isinstance(pdf_info, list):
        pages = pdf_info
        logger.warning("MinerU returned pdf_info as a list directly. Treating it as the pages list.")
    elif isinstance(pdf_info, dict):
        pages = pdf_info.get('pages', [])
    else:
        logger.error(f"Unexpected data type for pdf_info from MinerU: {type(pdf_info)}")
        pages = []

    if not pages:
        logger.warning(f"MinerU returned a valid structure but with no pages for '{filename}'.")
        return ""

    for page_num, page in enumerate(pages):
        content_parts.append(f"\n\n--- Page {page_num + 1} ---\n\n")
        blocks = page.get('blocks', [])
        for block in blocks:
            # Defensive coding: Ensure the block is a dictionary before processing.
            # The underlying MinerU library might return non-dict items in the blocks list.
            if not isinstance(block, dict):
                logger.warning(f"Skipping a non-dictionary block in '{filename}': {type(block)}")
                continue

            block_type = block.get('type')
            
            if block_type == 'text':
                content_parts.append(block.get('text', ''))
            elif block_type == 'table':
                html_content = block.get('html_content')
                if html_content:
                    markdown_table = linearize_html_table_to_markdown(html_content)
                    content_parts.append(f"\n\n{markdown_table}\n\n")
            elif block_type == 'figure':
                b64_data = block.get('b64_data')
                if b64_data:
                    try:
                        image_bytes = base64.b64decode(b64_data)
                        
                        # Per user spec: Process images first with PaddleOCR, then LatexOCR as fallback.
                        # This handles both text within images and mathematical formulas.
                        temp_filename = f"figure_{uuid.uuid4()}.png"
                        recognized_text = await _process_image_with_paddle(image_bytes, temp_filename)

                        if recognized_text and recognized_text.strip():
                            content_parts.append(f"\n[Image Text: {recognized_text.strip()}]\n")
                        else:
                            # If no general text is found, attempt to process it as a formula.
                            latex_code = await call_latexocr_service(image_bytes)
                            if latex_code:
                                content_parts.append(f"\n$${latex_code}$$\n")
                            else:
                                # If neither service returns content, add a placeholder.
                                content_parts.append(f"\n[Image: Figure block with no recognized text or formula]\n")
                    except Exception as e:
                        logger.error(f"Error processing figure block's b64_data: {e}")
            else:
                # Handle other potential block types if necessary
                if 'text' in block:
                    content_parts.append(block.get('text', ''))

    return "\n".join(content_parts)

async def _process_document_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Private method to orchestrate document processing from raw bytes.
    Routes the document to the appropriate service based on its file extension.
    This version uses a hybrid approach for PDFs: fast PyMuPDF first, then MinerU as fallback.
    """
    file_extension = os.path.splitext(filename)[1].lower()

    # HYBRID STRATEGY FOR PDFs
    if file_extension == '.pdf':
        # UNIFIED PDF STRATEGY (2025-07-21):
        # All PDFs are now routed directly to MinerU. The previous hybrid model (PyMuPDF fast-path)
        # was deprecated because the downstream RAG embedding process now relies on the
        # structured output (blocks, tables) from MinerU for semantic chunking.
        # Using PyMuPDF would bypass this crucial step, leading to suboptimal chunking.
        logger.info(f"Routing PDF '{filename}' to robust processor (MinerU) for semantic analysis.")
        return await _process_with_mineru(file_bytes, filename)

    # MinerU is the primary processor for Office documents
    elif file_extension in ['.docx', '.xlsx', '.pptx', '.doc']:
        logger.info(f"Routing document '{filename}' to primary processor (MinerU).")
        return await _process_with_mineru(file_bytes, filename)

    # Lightweight PaddleOCR is used for simple image-to-text tasks
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
        logger.info(f"Routing image file '{filename}' to lightweight PaddleOCR.")
        return await _process_image_with_paddle(file_bytes, filename)

    # Specialized extractors for other formats
    elif file_extension in ['.dwg', '.dxf']:
        logger.info(f"Routing CAD file '{filename}' to custom DWG extractor.")
        # Run the synchronous ezdxf function in a separate thread to avoid blocking
        return await asyncio.to_thread(extract_text_from_dwg, file_bytes, filename)

    else:
        logger.warning(f"Unsupported file type '{file_extension}' for file '{filename}'. Cannot process.")
        return ""

async def process_document(file: UploadFile) -> str:
    """
    Orchestrates the document processing pipeline from an UploadFile object.
    It sniffs the document type and routes it to the appropriate service (MinerU or PaddleOCR),
    then processes the results into a clean, linearized text format.

    :param file: The uploaded file from an API endpoint.
    :return: A string containing the processed document content.
    """
    logger.info(f"Starting document processing for file: {file.filename}")
    
    await file.seek(0)
    file_bytes = await file.read()
    
    # Delegate the core logic to the bytes-based processor
    return await _process_document_from_bytes(file_bytes, file.filename)