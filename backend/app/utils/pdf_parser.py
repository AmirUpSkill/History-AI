import fitz # --- this basically PyMuPDF --- 
from typing import Optional 
import logging 

# --- Set Up logging listen --- 
logger = logging.getLogger(__name__)

# --- Main Method --- 
def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """
        Extract text from a PDF file . 
        
        Args : 
            pdf_bytes: The PDF File content as bytes 
        Return : 
            The extracted text as a string ,,, or None if an error occurs . 
    """
    try:
        # --- Let's Open the PDF File --- 
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        # --- Extract Text from Each Page --- 
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text if text.strip() else None
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None