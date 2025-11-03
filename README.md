# 🦷 Accudent Lab Invoice Importer

A macOS drag-and-drop application for processing dental lab invoices (.pages and .pdf files).

## 🚀 Quick Start (For Non-Technical Users)

**Already installed?** Just double-click **"Accudent Importer"** on your Desktop!

**First time?** Run these two commands in Terminal:
```bash
cd ~/Code/accudent-bills
./install.sh
```

Then double-click the new desktop icon. See [QUICK_START.md](QUICK_START.md) for detailed instructions.

---

## Features

- **Drag & Drop**: Process multiple .pages and .pdf invoices simultaneously
- **Smart Parsing**: Extracts dentist name, patient name, due date, units, pricing, and costs
- **Multi-Format Output**: Generates XLSX, CSV, and PDF report
- **Monthly Organization**: Auto-organizes by month in `~/Documents/AccudentLab/YYYY-MM/`
- **Idempotent**: Re-running same invoices updates existing rows instead of duplicating
- **Print-Ready Reports**: Professional PDF reports with company header and dentist name
- **Auto-Cleanup**: Intermediate PDF files from .pages conversion are automatically deleted

## Installation

### Prerequisites

macOS with Homebrew installed. Install Python 3.12 with tkinter support:

```bash
brew install python@3.12 python-tk@3.12
```

### Setup

```bash
# Create virtual environment with Python 3.12
/opt/homebrew/bin/python3.12 -m venv venv

# Install dependencies
./venv/bin/pip install -r requirements.txt

# Run the app
./run.sh
```

Or if you prefer activating the venv:
```bash
source venv/bin/activate
pip install -r requirements.txt
python accudent_app.py
```

## Building macOS App

```bash
# Make the build script executable
chmod +x make_app.sh

# Build the .app bundle
./make_app.sh
```

The app will be created in the `dist/` folder.

## Output Format

Each monthly folder contains:
- `YYYY-MM_Accudent.xlsx` - Primary spreadsheet
- `YYYY-MM_Accudent.csv` - CSV mirror
- `YYYY-MM_Report.pdf` - Print-ready monthly report
- `logs/` - Processing logs

### Columns

1. **Date Due** - m/d/yyyy format
2. **Patient Name** - Extracted from invoice footer
3. **Total Units** - Sum of all quantities
4. **Unit Price** - Single price if uniform, blank if mixed
5. **Alloys/Extras Cost** - Sum of alloy/extras line items
6. **Total Cost** - Total from invoice

## Invoice Format

Invoices should contain:
- Table with columns: DESCRIPTION | QUANTITY | UNIT PRICE | COST
- Footer line: `Patient: {Name}, Due {m/d/yyyy}`

## Testing

Test the parser with a single invoice:
```bash
./venv/bin/python test_parsing.py "path/to/invoice.pages"
```

This will show you exactly what data is extracted before processing through the full app.

## Troubleshooting

### Pages Conversion Fails
- Ensure Pages app is installed on your Mac
- The app tries to extract `Preview.pdf` from the .pages package as a fallback
- If both fail, the file will appear in the Exceptions panel

### Text Extraction Issues
- The app tries PyObjC/PDFKit first (native macOS), then falls back to pypdf
- If extraction fails, check the logs in `~/Documents/AccudentLab/logs/`

### Parsing Errors
- Invoices must have the footer pattern: `Patient: {Name}, Due {m/d/yyyy}`
- Table must have all four column headers (DESCRIPTION, QUANTITY, UNIT PRICE, COST)
- Files with parsing errors appear in the Exceptions panel for manual review

### Build Issues
- This app requires Python 3.12 with tkinter
- If you see `ModuleNotFoundError: No module named '_tkinter'` or tcl-tk version errors:
  ```bash
  brew install python@3.12 python-tk@3.12
  rm -rf venv
  /opt/homebrew/bin/python3.12 -m venv venv
  ./venv/bin/pip install -r requirements.txt
  ```
- If pyobjc fails to install, try: `./venv/bin/pip install --upgrade pip setuptools wheel`

## Quick Start

```bash
# After installation, launch the app
./run.sh

# Or directly
./venv/bin/python accudent_app.py
```

## Usage

### Processing Invoices

1. **Launch the app** using `./run.sh` or the command above
2. **Drop files** - Click the drop zone or drag .pages/.pdf invoice files onto it
3. **Wait for processing** - Progress bar shows conversion, extraction, and parsing
4. **Review results**:
   - Click **"Open This Month's Sheet"** to view the Excel file
   - Click **"Open Report PDF"** to see the print-ready monthly report
   - Click **"Review Exceptions"** if any files failed to parse

### Settings

Click **"Settings…"** to configure:
- **Output Folder**: Where monthly folders are created (default: `~/Documents/AccudentLab/`)
- **CSV Mirror**: Toggle CSV file generation alongside XLSX
- **Month Override**: Force a specific month (leave blank to auto-detect from Due Date)

### Re-running Files

The app is **idempotent** - if you re-process the same invoice:
- It identifies duplicates by `(Date Due, Patient Name, Total Cost)`
- Updates the existing row instead of creating a duplicate
- Useful for correcting data or adding new invoices to an existing month
