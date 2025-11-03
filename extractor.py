"""
PDF text extraction utilities.
Tries PyObjC/PDFKit first, falls back to pypdf.
"""

import sys


def extract_text(pdf_path: str) -> str:
    """
    Extract text from PDF file.
    
    Tries PyObjC/PDFKit first (native macOS), falls back to pypdf.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If extraction fails
    """
    # Try PyObjC/PDFKit first (best for macOS)
    try:
        return _extract_with_pdfkit(pdf_path)
    except Exception as e:
        # Fallback to pypdf
        try:
            return _extract_with_pypdf(pdf_path)
        except Exception as e2:
            raise ValueError(
                f"Failed to extract text from {pdf_path}: "
                f"PDFKit failed ({e}), pypdf failed ({e2})"
            )


def _extract_with_pdfkit(pdf_path: str) -> str:
    """
    Extract text using macOS PDFKit via PyObjC.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
        
    Raises:
        ImportError: If PyObjC not available
        RuntimeError: If extraction fails
    """
    try:
        from Quartz import PDFDocument
        from Foundation import NSURL
    except ImportError:
        raise ImportError("PyObjC not available (install pyobjc-framework-Quartz)")
    
    # Load PDF
    url = NSURL.fileURLWithPath_(pdf_path)
    pdf_doc = PDFDocument.alloc().initWithURL_(url)
    
    if pdf_doc is None:
        raise RuntimeError(f"Could not load PDF: {pdf_path}")
    
    # Extract text from all pages
    text_parts = []
    page_count = pdf_doc.pageCount()
    
    for i in range(page_count):
        page = pdf_doc.pageAtIndex_(i)
        if page:
            page_text = page.string()
            if page_text:
                text_parts.append(page_text)
    
    if not text_parts:
        raise RuntimeError("No text extracted from PDF")
    
    return '\n\n'.join(text_parts)


def _extract_with_pypdf(pdf_path: str) -> str:
    """
    Extract text using pypdf library (fallback).
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
        
    Raises:
        ImportError: If pypdf not available
        RuntimeError: If extraction fails
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf not available (install pypdf)")
    
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        if not text_parts:
            raise RuntimeError("No text extracted from PDF")
        
        return '\n\n'.join(text_parts)
    
    except Exception as e:
        raise RuntimeError(f"pypdf extraction failed: {e}")
