# Developer Documentation

## Manual Installation

### Prerequisites

- macOS 10.15 or later
- Homebrew (https://brew.sh)
- Python 3.12 with tkinter support

### Install Python 3.12

```bash
brew install python@3.12 python-tk@3.12
```

### Setup Virtual Environment

```bash
# Create virtual environment with Python 3.12
/opt/homebrew/bin/python3.12 -m venv venv

# Activate the environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

**Option 1: Using the run script**
```bash
./run.sh
```

**Option 2: Direct Python execution**
```bash
./venv/bin/python3.12 accudent_app.py
```

**Option 3: Activated venv**
```bash
source venv/bin/activate
python accudent_app.py
```

## Testing

### Test Invoice Parsing

```bash
./venv/bin/python test_parsing.py "path/to/invoice.pages"
```

This shows extracted data without processing through the full app.

### Test with Sample Invoice

```bash
./venv/bin/python test_parsing.py "Dr. Aldredge          mm.pages"
```

## Project Structure

```
accudent-bills/
├── accudent_app.py          # Main GUI application
├── parser.py                # Invoice parsing logic
├── extractor.py             # PDF text extraction
├── converter.py             # .pages to PDF conversion
├── writer.py                # Excel/CSV file generation
├── report_generator.py      # PDF report creation
├── requirements.txt         # Python dependencies
├── run.sh                   # Launch script
├── FIRST_TIME_SETUP.sh      # Automated installer
├── install.sh               # Desktop icon installer
└── accudentlogo.png.png     # Company logo
```

## Dependencies

- **openpyxl** - Excel file generation
- **reportlab** - PDF report creation
- **pypdf** - PDF text extraction (fallback)
- **pyobjc-framework-Quartz** - macOS native PDF extraction
- **pyobjc-framework-Cocoa** - macOS .pages conversion

## Architecture

### Invoice Processing Flow

1. **File Input** - User drags .pages/.pdf files
2. **Conversion** - `.pages` → PDF (if needed)
3. **Extraction** - PDF → Text
4. **Parsing** - Text → Structured data
5. **Validation** - User confirms dentist name
6. **Writing** - Data → Excel/CSV/PDF
7. **Organization** - Files saved by month

### Parsing Logic

**Extracts:**
- Dentist name from "INVOICE FOR:" header
- Patient name and due date from footer
- Line items from table (Description, Quantity, Unit Price, Cost)

**Calculates:**
- Total Units: Always 1 (per business logic)
- Unit Price: First line item's unit price
- Alloys/Extras: Sum of costs from line items 2+
- Total Cost: Unit Price + Alloys/Extras

### Report Generation

- Logo centered at top
- Company info and statement title
- Clean black-and-white table design
- Summary totals and payment due date

## Troubleshooting

### ModuleNotFoundError: No module named '_tkinter'

```bash
brew install python-tk@3.12
rm -rf venv
/opt/homebrew/bin/python3.12 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Pages Conversion Fails

- Ensure Pages app is installed
- App tries to extract `Preview.pdf` from .pages package as fallback
- Check logs in `~/Documents/AccudentLab/logs/`

### Text Extraction Issues

- App tries PyObjC/PDFKit first (native macOS)
- Falls back to pypdf if native fails
- Both methods may fail on scanned PDFs (no OCR)

### Parsing Errors

**Invoice must have:**
- Footer: `Patient: {Name}, Due {m/d/yyyy}`
- Table headers: DESCRIPTION, QUANTITY, UNIT PRICE, COST
- At least one line item

**Common issues:**
- Spaced-out text from PDF extraction
- Missing required sections
- Malformed dates

## Building Distribution

### Create Desktop Icon

```bash
./install.sh
```

Creates `.app` bundle on Desktop pointing to current installation.

### Full Setup (Fresh Install)

```bash
./FIRST_TIME_SETUP.sh
```

Installs everything from scratch including Homebrew and Python.

## Code Style

- Follow PEP 8
- Use type hints where practical
- Document complex logic
- Keep functions focused and testable

## Git Workflow

```bash
# Create feature branch
git checkout -b feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature-name
```

## License

MIT License - See LICENSE file for details
