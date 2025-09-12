import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

def is_scanned_pdf(pdf_bytes: bytes) -> bool:
    """
    Checks if a PDF is likely scanned (i.e., contains no selectable text).
    This is a crucial first step in the document processing pipeline to decide
    whether to use MinerU (for text-based PDFs) or PaddleOCR (for image-based PDFs).

    Args:
        pdf_bytes: The content of the PDF file as bytes.

    Returns:
        True if the PDF is likely scanned, False otherwise.
    """
    doc = None
    try:
        # Open the PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # If the document is empty, it's not a scanned PDF in a meaningful way
        if len(doc) == 0:
            logger.warning("Received an empty PDF (0 pages).")
            return False

        # Check the first page for any extractable text
        page = doc[0]
        text = page.get_text().strip()

        # If there's no text, it's highly likely a scanned/image-based PDF
        is_scanned = len(text) == 0
        if is_scanned:
            logger.info("PDF detected as scanned (no text found on first page).")
        else:
            logger.info("PDF detected as text-based.")
        
        return is_scanned

    except Exception as e:
        # If any error occurs during parsing (e.g., corrupted file),
        # it's safer to treat it as a case for OCR.
        logger.error(f"Error parsing PDF to check for text, assuming it's scanned. Error: {e}")
        return True
    finally:
        # Ensure the document is closed to free up resources
        if doc:
            doc.close()