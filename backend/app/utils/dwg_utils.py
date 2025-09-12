import logging
import tempfile
import os
import ezdxf
from ezdxf import DXFStructureError

logger = logging.getLogger(__name__)

def extract_text_from_dwg(file_bytes: bytes, filename: str) -> str:
    """
    Extracts all text entities from a DWG or DXF file's byte content.

    It writes the bytes to a temporary file to be read by ezdxf, then extracts
    text from TEXT and MTEXT entities in the modelspace.

    :param file_bytes: The byte content of the DWG/DXF file.
    :param filename: The original name of the file, used for creating a temp file with the correct extension.
    :return: A single string containing all extracted text, separated by newlines.
    """
    # ezdxf needs to read from a file path, so we use a temporary file.
    # We preserve the extension to help ezdxf identify the format.
    suffix = os.path.splitext(filename)[1]
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
            fp.write(file_bytes)
            temp_file_path = fp.name
        
        logger.info(f"Loading DWG/DXF from temporary file: {temp_file_path}")
        
        # Load the DXF document
        doc = ezdxf.readfile(temp_file_path)
        msp = doc.modelspace()
        
        # Extract text from TEXT and MTEXT entities
        extracted_texts = []
        for entity in msp.query('TEXT MTEXT'):
            if entity.dxftype() == 'TEXT':
                text = entity.dxf.text
                if text.strip():
                    extracted_texts.append(text.strip())
            elif entity.dxftype() == 'MTEXT':
                # MTEXT can have complex formatting, plain_text() helps to simplify it.
                text = entity.plain_text()
                if text.strip():
                    extracted_texts.append(text.strip())
                    
        logger.info(f"Extracted {len(extracted_texts)} text blocks from '{filename}'.")
        return "\n".join(extracted_texts)

    except (IOError, DXFStructureError, FileNotFoundError) as e:
        logger.error(f"Could not process DWG/DXF file '{filename}'. It might be corrupted, an unsupported version, or not a valid DXF/DWG file. Error: {e}")
        # Return empty string on failure to prevent downstream errors
        return ""
    except ImportError:
        logger.error("The 'ezdxf' library is required to process DWG/DXF files. Please install it using 'pip install ezdxf'.")
        return "Error: ezdxf library not found."
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing DWG/DXF file '{filename}': {e}")
        return ""
    finally:
        # Clean up the temporary file
        if temp_file and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Removed temporary file: {temp_file_path}")
