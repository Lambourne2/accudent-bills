"""
PDF report generation using reportlab.
Creates print-ready monthly reports with tables and totals.
"""

import subprocess
import unicodedata
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


def remove_ligatures(text: str) -> str:
    """
    Remove ligature characters that may not render properly in PDFs.
    Converts ligatures like ﬀ, ﬁ, ﬂ to their component letters.
    """
    # Map ligatures to their component characters
    ligature_map = {
        '\ufb00': 'ff',  # ﬀ
        '\ufb01': 'fi',  # ﬁ
        '\ufb02': 'fl',  # ﬂ
        '\ufb03': 'ffi', # ﬃ
        '\ufb04': 'ffl', # ﬄ
        '\ufb05': 'ft',  # ﬅ (long s + t)
        '\ufb06': 'st',  # ﬆ
    }
    
    # Replace ligatures
    for ligature, replacement in ligature_map.items():
        text = text.replace(ligature, replacement)
    
    # Also normalize to NFD and remove combining characters that might cause issues
    text = unicodedata.normalize('NFC', text)
    
    return text


def build_report_pdf(month_folder: Path, rows: List[Dict]) -> Path:
    """
    Build print-ready PDF report for the month.
    
    Args:
        month_folder: Path to month folder
        rows: List of invoice dicts (should be sorted by date_due)
        
    Returns:
        Path to generated PDF
    """
    pdf_path = month_folder / f"{month_folder.name}_Report.pdf"
    
    # Sort rows by date
    sorted_rows = sorted(rows, key=lambda r: r['date_due'])
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
    )
    
    # Build content
    story = []
    styles = getSampleStyleSheet()
    
    # Extract dentist name from first row (all invoices should be from same dentist)
    dentist_name = sorted_rows[0]['dentist_name'] if sorted_rows else 'Unknown Dentist'
    dentist_name = remove_ligatures(dentist_name)  # Fix ligature rendering issues
    
    # Extract month/year from folder name (YYYY-MM) and get last day of month
    year_month = month_folder.name
    month_obj = datetime.strptime(year_month, '%Y-%m')
    
    # Get last day of the month
    if month_obj.month == 12:
        last_day = month_obj.replace(day=31)
    else:
        next_month = month_obj.replace(month=month_obj.month + 1, day=1)
        from datetime import timedelta
        last_day = next_month - timedelta(days=1)
    
    last_day_str = last_day.strftime('%-m/%-d/%Y')
    
    # Add logo at top (centered)
    logo_path = Path(__file__).parent / "accudentlogo.png.png"
    if logo_path.exists():
        logo = Image(str(logo_path), width=1.2*inch, height=1.2*inch)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 0.15*inch))
    
    # Company name style - clean black text
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        spaceAfter=4,
    )
    
    # Address style - lighter weight
    address_style = ParagraphStyle(
        'Address',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.black,
        spaceAfter=0.15*inch,
    )
    
    # Statement title style - clean and minimal
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        spaceAfter=0.25*inch,
    )
    
    # Build header
    story.append(Paragraph("Accudent Dental Lab", company_style))
    story.append(Paragraph("5283 West 8180 South, West Jordan, Utah · Phone 801-231-6161", address_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Statement for period ending {last_day_str} for {dentist_name}", title_style))
    
    # Build table data
    table_data = [
        ['Date Due', 'Patient Name', 'Total Units', 'Unit Price', 'Alloys/Extras Cost', 'Total Cost']
    ]
    
    # Calculate totals
    total_cost_sum = sum(row['total_cost'] for row in sorted_rows)
    
    for row in sorted_rows:
        # Format date as m/d/yyyy
        date_str = row['date_due'].strftime('%-m/%-d/%Y')
        
        # Format unit price (blank if None)
        unit_price_str = f"${row['unit_price']:.2f}" if row['unit_price'] else ''
        
        table_data.append([
            date_str,
            remove_ligatures(row['patient_name']),
            str(row['total_units']),
            unit_price_str,
            f"${row['alloys_extras_cost']:.2f}",
            f"${row['total_cost']:.2f}",
        ])
    
    # Add total row at the bottom
    table_data.append([
        '',
        '',
        '',
        '',
        'TOTAL:',
        f"${total_cost_sum:.2f}",
    ])
    
    # Create table
    table = Table(table_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1.3*inch, 1*inch])
    
    # Get row count for styling (header + data rows + total row)
    last_row_idx = len(table_data) - 1
    
    # Style table - clean black theme with no fills
    table.setStyle(TableStyle([
        # Header row - bold text, no background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
        
        # Data rows - clean black text, no backgrounds
        ('TEXTCOLOR', (0, 1), (-1, last_row_idx - 1), colors.black),
        ('ALIGN', (0, 1), (0, last_row_idx - 1), 'CENTER'),  # Date Due centered
        ('ALIGN', (2, 1), (-1, last_row_idx - 1), 'RIGHT'),  # Numbers right-aligned
        ('FONTNAME', (0, 1), (-1, last_row_idx - 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, last_row_idx - 1), 9),
        ('TOPPADDING', (0, 1), (-1, last_row_idx - 1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, last_row_idx - 1), 7),
        
        # Total row - bold, clean
        ('FONTNAME', (0, last_row_idx), (-1, last_row_idx), 'Helvetica-Bold'),
        ('FONTSIZE', (0, last_row_idx), (-1, last_row_idx), 10),
        ('ALIGN', (4, last_row_idx), (-1, last_row_idx), 'RIGHT'),
        ('TOPPADDING', (0, last_row_idx), (-1, last_row_idx), 10),
        ('BOTTOMPADDING', (0, last_row_idx), (-1, last_row_idx), 8),
        ('LINEABOVE', (0, last_row_idx), (-1, last_row_idx), 1.5, colors.black),
        
        # Outer border only - clean lines
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        
        # Vertical lines between columns
        ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.black),
        ('LINEAFTER', (1, 0), (1, -1), 0.5, colors.black),
        ('LINEAFTER', (2, 0), (2, -1), 0.5, colors.black),
        ('LINEAFTER', (3, 0), (3, -1), 0.5, colors.black),
        ('LINEAFTER', (4, 0), (4, -1), 0.5, colors.black),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer with summary statistics - clean and minimal
    total_patients = len(sorted_rows)
    total_units = sum(row['total_units'] for row in sorted_rows)
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=3,
    )
    
    # Thank you message
    story.append(Spacer(1, 0.3*inch))
    
    thank_you_style = ParagraphStyle(
        'ThankYou',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    
    questions_style = ParagraphStyle(
        'Questions',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    story.append(Paragraph("THANK YOU", thank_you_style))
    story.append(Paragraph("Questions call 801-231-6161", questions_style))
    
    # Payment due date - 25th of next month
    story.append(Spacer(1, 0.1*inch))
    
    # Calculate payment due date (25th of following month)
    if last_day.month == 12:
        payment_due = last_day.replace(year=last_day.year + 1, month=1, day=25)
    else:
        payment_due = last_day.replace(month=last_day.month + 1, day=25)
    
    payment_due_str = payment_due.strftime('%-m/%-d/%Y')
    
    payment_style = ParagraphStyle(
        'Payment',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.black,
    )
    
    story.append(Paragraph(f"Payment due by: {payment_due_str}", payment_style))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path


def open_pdf_in_preview(pdf_path: Path):
    """
    Open PDF in macOS Preview app.
    
    Args:
        pdf_path: Path to PDF file
    """
    try:
        subprocess.run(['open', '-a', 'Preview', str(pdf_path)], check=True)
    except subprocess.CalledProcessError as e:
        # Fallback to default app
        subprocess.run(['open', str(pdf_path)])
