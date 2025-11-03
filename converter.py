"""
PDF conversion utilities for .pages files.
Uses AppleScript to convert .pages to .pdf via Pages app.
"""

import os
import subprocess
import tempfile
import zipfile
from pathlib import Path


def ensure_pdf(file_path: str) -> str:
    """
    Ensure we have a PDF file. If input is .pages, convert it.
    
    Args:
        file_path: Path to .pages or .pdf file
        
    Returns:
        Path to PDF file (original or converted)
        
    Raises:
        ValueError: If conversion fails
    """
    path = Path(file_path)
    
    # Already a PDF
    if path.suffix.lower() == '.pdf':
        return str(path)
    
    # .pages file - try conversion
    if path.suffix.lower() == '.pages':
        # Try AppleScript conversion first
        try:
            return _convert_pages_applescript(str(path))
        except Exception as e:
            # Fallback: try extracting embedded Preview.pdf from .pages package
            try:
                return _extract_preview_pdf(str(path))
            except Exception as e2:
                raise ValueError(
                    f"Failed to convert {path.name}: AppleScript failed ({e}), "
                    f"Preview.pdf extraction failed ({e2})"
                )
    
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _convert_pages_applescript(pages_path: str) -> str:
    """
    Convert .pages to .pdf using AppleScript and Pages app.
    
    Args:
        pages_path: Path to .pages file
        
    Returns:
        Path to converted PDF file
        
    Raises:
        RuntimeError: If conversion fails
    """
    pages_path = os.path.abspath(pages_path)
    pdf_path = pages_path.replace('.pages', '.pdf')
    
    # If PDF already exists from previous run, use it
    if os.path.exists(pdf_path):
        return pdf_path
    
    # AppleScript to convert via Pages
    applescript = f'''
on run argv
    set inPath to POSIX file "{pages_path}" as alias
    set outPath to POSIX file "{pdf_path}"
    tell application "Pages"
        set docRef to open inPath
        export docRef to outPath as PDF
        close docRef saving no
    end tell
end run
'''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript error: {result.stderr}")
        
        if not os.path.exists(pdf_path):
            raise RuntimeError("PDF was not created")
        
        return pdf_path
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("Conversion timed out after 30 seconds")
    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}")


def _extract_preview_pdf(pages_path: str) -> str:
    """
    Extract Preview.pdf from .pages package (fallback method).
    
    .pages files are actually zip archives containing QuickLook/Preview.pdf
    
    Args:
        pages_path: Path to .pages file
        
    Returns:
        Path to extracted PDF
        
    Raises:
        ValueError: If Preview.pdf not found
    """
    try:
        with zipfile.ZipFile(pages_path, 'r') as z:
            # Look for QuickLook/Preview.pdf
            preview_files = [name for name in z.namelist() 
                           if 'Preview.pdf' in name or 'preview.pdf' in name]
            
            if not preview_files:
                raise ValueError("No Preview.pdf found in .pages package")
            
            # Extract to temp location
            preview_name = preview_files[0]
            temp_dir = tempfile.mkdtemp()
            z.extract(preview_name, temp_dir)
            
            # Move to same location as .pages file with .pdf extension
            pdf_path = pages_path.replace('.pages', '.pdf')
            extracted = os.path.join(temp_dir, preview_name)
            os.rename(extracted, pdf_path)
            
            # Cleanup temp dir
            os.rmdir(temp_dir)
            
            return pdf_path
    
    except zipfile.BadZipFile:
        raise ValueError(f"{pages_path} is not a valid .pages file")
