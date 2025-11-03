"""
XLSX and CSV writing with proper formatting and idempotent updates.
"""

import csv
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

import openpyxl
from openpyxl.styles import numbers, Font, Alignment, Border, Side


COLUMN_HEADERS = [
    'Date Due',
    'Patient Name',
    'Total Cost',
]


def get_month_folder(date_due: datetime, base_path: str = None) -> Path:
    """
    Get the folder path for a given month.
    
    Args:
        date_due: Date to determine month
        base_path: Base output path (default ~/Documents/AccudentLab/)
        
    Returns:
        Path to month folder
    """
    if base_path is None:
        base_path = os.path.expanduser('~/Documents/AccudentLab')
    
    base = Path(base_path)
    month_folder = base / date_due.strftime('%Y-%m')
    month_folder.mkdir(parents=True, exist_ok=True)
    
    # Create logs subfolder
    (month_folder / 'logs').mkdir(exist_ok=True)
    
    return month_folder


def write_xlsx(month_folder: Path, rows: List[Dict]) -> Path:
    """
    Write or update XLSX file with invoice data.
    
    Idempotent: Updates existing rows matching (date_due, patient_name, total_cost).
    
    Args:
        month_folder: Path to month folder
        rows: List of parsed invoice dicts
        
    Returns:
        Path to XLSX file
    """
    xlsx_path = month_folder / f"{month_folder.name}_Accudent.xlsx"
    
    # Load existing workbook or create new
    if xlsx_path.exists():
        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Accudent'
        # Write headers
        for col_idx, header in enumerate(COLUMN_HEADERS, start=1):
            ws.cell(row=1, column=col_idx, value=header)
    
    # Build lookup of existing rows: (date_due, patient_name, total_cost) -> row_idx
    existing_rows = {}
    for row_idx in range(2, ws.max_row + 1):
        date_val = ws.cell(row=row_idx, column=1).value
        name_val = ws.cell(row=row_idx, column=2).value
        total_val = ws.cell(row=row_idx, column=6).value
        
        if date_val and name_val and total_val:
            # Convert date to string for comparison
            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
            
            # Convert total to Decimal
            total_dec = Decimal(str(total_val))
            
            key = (date_str, name_val, total_dec)
            existing_rows[key] = row_idx
    
    # Process each row: update if exists, append if new
    for row_data in rows:
        date_str = row_data['date_due'].strftime('%Y-%m-%d')
        key = (date_str, row_data['patient_name'], row_data['total_cost'])
        
        if key in existing_rows:
            # Update existing row
            row_idx = existing_rows[key]
        else:
            # Append new row
            row_idx = ws.max_row + 1
        
        _write_row(ws, row_idx, row_data)
    
    # Sort by Date Due (column A)
    _sort_by_date(ws)
    
    # Apply formatting
    _apply_formats(ws)
    
    # Save
    wb.save(xlsx_path)
    
    return xlsx_path


def _write_row(ws, row_idx: int, row_data: Dict):
    """Write a single data row to worksheet."""
    # A: Date Due (datetime object, will be formatted)
    ws.cell(row=row_idx, column=1, value=row_data['date_due'])
    
    # B: Patient Name
    ws.cell(row=row_idx, column=2, value=row_data['patient_name'])
    
    # C: Total Cost
    ws.cell(row=row_idx, column=3, value=float(row_data['total_cost']))


def _sort_by_date(ws):
    """Sort worksheet by Date Due (column A) ascending."""
    # Get all data rows (skip header)
    data_rows = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        # Only include rows with data
        if row[0].value:  # Has date
            data_rows.append([cell.value for cell in row])
    
    if not data_rows:
        return
    
    # Sort by first column (date)
    data_rows.sort(key=lambda r: r[0] if isinstance(r[0], datetime) else datetime.max)
    
    # Write back sorted data
    for idx, row_data in enumerate(data_rows, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=idx, column=col_idx)
            # Re-apply formula for column G
            if col_idx == 7 and isinstance(value, str) and value.startswith('='):
                cell.value = value
            else:
                cell.value = value


def _apply_formats(ws):
    """Apply number formats and styling to columns."""
    # Define styles
    header_font = Font(name='Helvetica', size=11, bold=True)
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    data_font = Font(name='Helvetica', size=10)
    center_alignment = Alignment(horizontal='center', vertical='center')
    right_alignment = Alignment(horizontal='right', vertical='center')
    left_alignment = Alignment(horizontal='left', vertical='center')
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Style header row
    for col_idx in range(1, 4):  # 3 columns only
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Format and style data rows
    for row_idx in range(2, ws.max_row + 1):
        # A: Date as m/d/yyyy
        cell_a = ws.cell(row=row_idx, column=1)
        cell_a.number_format = 'M/D/YYYY'
        cell_a.alignment = center_alignment
        cell_a.font = data_font
        cell_a.border = thin_border
        
        # B: Patient Name
        cell_b = ws.cell(row=row_idx, column=2)
        cell_b.alignment = left_alignment
        cell_b.font = data_font
        cell_b.border = thin_border
        
        # C: Total Cost as currency
        cell_c = ws.cell(row=row_idx, column=3)
        cell_c.number_format = '$#,##0.00'
        cell_c.alignment = right_alignment
        cell_c.font = data_font
        cell_c.border = thin_border
    
    # Set column widths for better readability
    ws.column_dimensions['A'].width = 15  # Date Due
    ws.column_dimensions['B'].width = 30  # Patient Name
    ws.column_dimensions['C'].width = 15  # Total Cost
    
    # Freeze header row for scrolling
    ws.freeze_panes = 'A2'
    
    # Enable auto-filter on header row
    ws.auto_filter.ref = f'A1:C{ws.max_row}'


def write_csv(month_folder: Path, rows: List[Dict]) -> Path:
    """
    Write CSV mirror of XLSX (3 columns only).
    
    Args:
        month_folder: Path to month folder
        rows: List of parsed invoice dicts (should be sorted)
        
    Returns:
        Path to CSV file
    """
    csv_path = month_folder / f"{month_folder.name}_Accudent.csv"
    
    # Sort rows by date
    sorted_rows = sorted(rows, key=lambda r: r['date_due'])
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(COLUMN_HEADERS)
        
        # Write data rows
        for row_data in sorted_rows:
            # Format date as m/d/yyyy
            date_str = row_data['date_due'].strftime('%-m/%-d/%Y')
            
            writer.writerow([
                date_str,
                row_data['patient_name'],
                f"${row_data['total_cost']:.2f}",
            ])
    
    return csv_path


def load_existing_rows(month_folder: Path) -> List[Dict]:
    """
    Load existing rows from XLSX if it exists.
    
    Args:
        month_folder: Path to month folder
        
    Returns:
        List of row dicts
    """
    xlsx_path = month_folder / f"{month_folder.name}_Accudent.xlsx"
    
    if not xlsx_path.exists():
        return []
    
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    
    rows = []
    for row_idx in range(2, ws.max_row + 1):
        date_val = ws.cell(row=row_idx, column=1).value
        if not date_val:
            continue
        
        rows.append({
            'dentist_name': '',  # Not stored in Excel, only used for PDF report
            'date_due': date_val if isinstance(date_val, datetime) else datetime.strptime(str(date_val), '%Y-%m-%d'),
            'patient_name': ws.cell(row=row_idx, column=2).value,
            'total_cost': Decimal(str(ws.cell(row=row_idx, column=3).value or 0)),
        })
    
    return rows
