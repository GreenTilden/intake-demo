"""OCR service — extract text from scanned letters and PDFs.

Uses Tesseract (CPU-only, no GPU needed). Handles:
- Scanned PDFs (converted to images via poppler/pdf2image)
- Direct image uploads (JPG, PNG, TIFF)
- Multi-page documents (concatenates all pages)
"""
import tempfile
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


SUPPORTED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}
SUPPORTED_PDF_TYPES = {".pdf"}
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | SUPPORTED_PDF_TYPES


def extract_text(file_path: str) -> str:
    """Extract text from a scanned document or PDF.

    Returns the full extracted text, one page per section separated by newlines.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in SUPPORTED_PDF_TYPES:
        return _extract_from_pdf(file_path)
    elif suffix in SUPPORTED_IMAGE_TYPES:
        return _extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_from_pdf(pdf_path: str) -> str:
    """Convert PDF pages to images, OCR each page."""
    images = convert_from_path(pdf_path, dpi=300)
    pages = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang="eng")
        if text.strip():
            pages.append(text.strip())
    return "\n\n---\n\n".join(pages)


def _extract_from_image(image_path: str) -> str:
    """OCR a single image file."""
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang="eng").strip()


def is_supported(filename: str) -> bool:
    """Check if the file type is supported for OCR."""
    return Path(filename).suffix.lower() in SUPPORTED_TYPES
