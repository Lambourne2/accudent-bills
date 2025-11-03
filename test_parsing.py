#!/usr/bin/env python3
"""
Quick test script to verify parsing works with sample invoice.
"""

import sys
from pathlib import Path
from converter import ensure_pdf
from extractor import extract_text
from parser import parse_invoice

def test_invoice(file_path):
    """Test parsing a single invoice."""
    print(f"Testing: {file_path}\n")
    
    # Convert to PDF
    print("1. Converting to PDF...")
    original_path = Path(file_path)
    pdf_path = ensure_pdf(file_path)
    print(f"   PDF: {pdf_path}\n")
    
    # Mark for cleanup if we converted from .pages
    cleanup_pdf = original_path.suffix.lower() == '.pages' and pdf_path != file_path
    
    try:
        # Extract text
        print("2. Extracting text...")
        text = extract_text(pdf_path)
        print(f"   Extracted {len(text)} characters")
        print(f"   First 500 chars:\n{text[:500]}\n")
        
        # Parse invoice
        print("3. Parsing invoice...")
        data = parse_invoice(text)
        print("   ✓ Parsed successfully!")
        print()
        print("   Results:")
        print(f"   - Dentist Name: {data['dentist_name']}")
        print(f"   - Patient Name: {data['patient_name']}")
        print(f"   - Date Due: {data['date_due'].strftime('%m/%d/%Y')}")
        print(f"   - Total Cost: ${data['total_cost']:.2f}")
        
        success = True
    except Exception as e:
        print(f"   ✗ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    finally:
        # Clean up intermediate PDF
        if cleanup_pdf and Path(pdf_path).exists():
            Path(pdf_path).unlink()
            print(f"\n4. Cleaned up intermediate PDF: {pdf_path}")
    
    return success

if __name__ == '__main__':
    file_path = sys.argv[1] if len(sys.argv) > 1 else "Dr. Aldredge          mm.pages"
    success = test_invoice(file_path)
    sys.exit(0 if success else 1)
