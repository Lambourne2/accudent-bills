# Project Structure

```
accudent-bills/
├── accudent_app.py           # Main GUI application (Tkinter)
├── converter.py              # .pages → .pdf conversion (AppleScript)
├── extractor.py              # PDF text extraction (PyObjC/pypdf)
├── parser.py                 # Invoice parsing logic (regex, table extraction)
├── writer.py                 # XLSX/CSV writing (openpyxl)
├── report_generator.py       # PDF report generation (reportlab)
├── test_parsing.py           # Quick test script for single invoices
├── run.sh                    # Launcher script
├── make_app.sh               # PyInstaller build script
├── requirements.txt          # Python dependencies
├── README.md                 # User documentation
├── EXAMPLE_OUTPUT.md         # Output format examples
├── PROJECT_STRUCTURE.md      # This file
├── .gitignore                # Git ignore rules
├── venv/                     # Virtual environment (created by user)
├── ExampleSheet.xlsx         # Sample output format
└── Dr. Aldredge mm.pages     # Sample invoice for testing
```

## Core Modules

### `accudent_app.py`
Main GUI application with:
- Tkinter window with drop zone
- File processing worker thread
- Progress tracking
- Settings dialog
- Exceptions panel for manual review
- Buttons to open sheets and reports

**Entry point:** Run with `./run.sh` or `./venv/bin/python accudent_app.py`

### `converter.py`
Handles .pages → .pdf conversion:
- Primary method: AppleScript calling Pages app
- Fallback: Extract `Preview.pdf` from .pages package (zip archive)
- Returns path to PDF file

**Key function:** `ensure_pdf(file_path) -> str`

### `extractor.py`
Extracts text from PDF files:
- Primary method: PyObjC/PDFKit (native macOS)
- Fallback: pypdf library
- Returns full text from all pages

**Key function:** `extract_text(pdf_path) -> str`

### `parser.py`
Parses invoice text and extracts structured data:
- **Patient & Date:** Regex pattern `Patient: {Name}, Due {m/d/yyyy}`
- **Table:** Finds header row, parses subsequent data rows
- **Totals:** Computes units, pricing, alloys/extras, total cost
- Handles spaced-out headers (e.g., "D E S C R I P T I O N")

**Key function:** `parse_invoice(text) -> Dict`

Returns:
```python
{
    'date_due': datetime,
    'patient_name': str,
    'total_units': int,
    'unit_price': Decimal | None,  # None if mixed prices
    'alloys_extras_cost': Decimal,
    'total_cost': Decimal,
}
```

### `writer.py`
Writes data to XLSX and CSV files:
- **Idempotent updates:** Uses `(date_due, patient_name, total_cost)` as unique key
- **XLSX formatting:**
  - Date: `m/d/yyyy`
  - Currency: `$#,##0.00`
  - Hidden column G with formula for legacy parity
- **Sorting:** Always sorts by Date Due ascending
- **CSV:** Mirrors columns A-F from XLSX

**Key functions:**
- `write_xlsx(month_folder, rows) -> Path`
- `write_csv(month_folder, rows) -> Path`
- `get_month_folder(date_due, base_path) -> Path`

### `report_generator.py`
Generates print-ready PDF reports:
- Table with all 6 columns
- Header: "Accudent Dental Lab — {Month Year}"
- Footer totals: Patients, Units, Total Cost, Alloys/Extras
- Professional styling with alternating row colors
- Auto-opens in Preview

**Key functions:**
- `build_report_pdf(month_folder, rows) -> Path`
- `open_pdf_in_preview(pdf_path)`

## Helper Scripts

### `test_parsing.py`
Standalone test script to verify parsing on a single invoice:
```bash
./venv/bin/python test_parsing.py "invoice.pages"
```

Shows:
1. PDF conversion status
2. Extracted text preview
3. Parsed data fields

### `run.sh`
Quick launcher that checks for venv and runs the app:
```bash
./run.sh
```

### `make_app.sh`
PyInstaller build script to create macOS `.app` bundle:
```bash
./make_app.sh
```

Creates: `dist/Accudent Importer.app`

## Data Flow

```
1. User drops files → accudent_app.py
2. For each file:
   a. converter.ensure_pdf() → PDF path
   b. extractor.extract_text() → text string
   c. parser.parse_invoice() → structured dict
   d. Group by month (date_due)
3. For each month:
   a. writer.write_xlsx() → XLSX file
   b. writer.write_csv() → CSV file (if enabled)
   c. report_generator.build_report_pdf() → PDF report
4. Auto-open report in Preview
5. Enable "Open Sheet" and "Open Report" buttons
```

## Dependencies

See `requirements.txt`:
- **openpyxl:** Excel file creation with formatting
- **reportlab:** PDF report generation
- **pypdf:** PDF text extraction (fallback)
- **pyobjc-framework-Quartz:** macOS PDFKit integration
- **pyobjc-framework-Cocoa:** macOS native APIs

## Output Location

Default: `~/Documents/AccudentLab/YYYY-MM/`

Each month folder contains:
- `YYYY-MM_Accudent.xlsx`
- `YYYY-MM_Accudent.csv`
- `YYYY-MM_Report.pdf`
- `logs/` with timestamped run logs

## Error Handling

- **Conversion failures:** Fallback to Preview.pdf extraction
- **Extraction failures:** Try PDFKit, fallback to pypdf
- **Parsing errors:** Add to exceptions panel for manual review
- **All errors:** Logged to `logs/accudent_TIMESTAMP.log`
