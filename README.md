# 🦷 Accudent Lab Invoice Importer

A macOS drag-and-drop application for processing dental lab invoices (.pages and .pdf files).

## 🚀 Quick Start (For Non-Technical Users)

### Already Installed?
Just **right-click** **"Accudent Importer"** on your Desktop → **Open**

### First Time Setup?

**1. Download this repository**
```bash
# Click the green "Code" button above → Download ZIP
# Unzip it anywhere on your Mac (Desktop, Documents, etc.)
```

**2. Open Terminal** (search "Terminal" in Spotlight)

**3. Run the setup script**
```bash
# Navigate to wherever you unzipped the folder
cd ~/Downloads/accudent-bills-main    # (or wherever you put it)

# Run setup (this installs everything)
./FIRST_TIME_SETUP.sh
```

**4. Launch the app**
- Find "Accudent Importer" on your Desktop
- **Right-click** → **Open** (first time only)
- After that, just double-click!

📖 See [INSTRUCTIONS_FOR_USER.md](INSTRUCTIONS_FOR_USER.md) for detailed usage guide.

---

## Features

- **Drag & Drop**: Process multiple .pages and .pdf invoices simultaneously
- **Smart Parsing**: Extracts dentist name, patient name, due date, units, pricing, and costs
- **Multi-Format Output**: Generates XLSX, CSV, and PDF report
- **Monthly Organization**: Auto-organizes by month in `~/Documents/AccudentLab/YYYY-MM/`
- **Idempotent**: Re-running same invoices updates existing rows instead of duplicating
- **Print-Ready Reports**: Professional PDF reports with company header and dentist name
- **Auto-Cleanup**: Intermediate PDF files from .pages conversion are automatically deleted

## Installation (Automated)

The `FIRST_TIME_SETUP.sh` script automatically installs:
- ✅ Homebrew (if not installed)
- ✅ Python 3.12 with tkinter
- ✅ Virtual environment
- ✅ All dependencies
- ✅ Desktop launcher

**No manual installation required!** Just run the setup script once.

For developers or manual installation, see [DEVELOPERS.md](DEVELOPERS.md).

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
