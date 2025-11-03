# Quick Start Guide

## First-Time Setup (5 minutes)

### 1. Install Python 3.12 with Tkinter

```bash
brew install python@3.12 python-tk@3.12
```

### 2. Install Dependencies

```bash
cd /Users/peytonlambourne/Code/accudent-bills

# Create virtual environment with Python 3.12
/opt/homebrew/bin/python3.12 -m venv venv

# Install packages
./venv/bin/pip install -r requirements.txt
```

### 3. Test with Sample Invoice

```bash
# Verify parsing works
./venv/bin/python test_parsing.py "Dr. Aldredge          mm.pages"
```

Expected output:
```
Testing: Dr. Aldredge          mm.pages

1. Converting to PDF...
   PDF: /Users/.../Dr. Aldredge          mm.pdf

2. Extracting text...
   Extracted 285 characters

3. Parsing invoice...
   ✓ Parsed successfully!

   Results:
   - Patient Name: Marcia Miller
   - Date Due: 10/07/2025
   - Total Units: 1
   - Unit Price: $100.00
   - Alloys/Extras: $0.00
   - Total Cost: $100.00
```

### 4. Launch the App

```bash
./run.sh
```

A window titled "Accudent Importer" will appear.

## Using the App

### Basic Workflow

1. **Click the drop zone** (or drag files onto it)
2. **Select one or more .pages/.pdf files**
3. **Wait** - Progress bar shows: Converting → Extracting → Parsing → Writing → Building Report
4. **When done:**
   - Status shows "✓ All files processed successfully" (green)
   - "Open This Month's Sheet" button becomes active
   - "Open Report PDF" button becomes active
   - Report PDF opens automatically in Preview

### First Run Example

Process the sample invoice:

1. Click drop zone
2. Select `Dr. Aldredge          mm.pages`
3. Wait ~5 seconds
4. Report opens showing:
   - 1 patient (Marcia Miller)
   - 1 unit
   - $100.00 total

Files created in `~/Documents/AccudentLab/2025-10/`:
- `2025-10_Accudent.xlsx`
- `2025-10_Accudent.csv`
- `2025-10_Report.pdf`

### Processing Multiple Invoices

1. Drop 10+ invoice files at once
2. App processes them in sequence
3. Groups by month automatically
4. Each month gets its own folder

Example: If you drop invoices with due dates in Oct, Nov, and Dec:

```
~/Documents/AccudentLab/
├── 2025-10/
│   ├── 2025-10_Accudent.xlsx
│   ├── 2025-10_Accudent.csv
│   └── 2025-10_Report.pdf
├── 2025-11/
│   ├── 2025-11_Accudent.xlsx
│   ├── 2025-11_Accudent.csv
│   └── 2025-11_Report.pdf
└── 2025-12/
    ├── 2025-12_Accudent.xlsx
    ├── 2025-12_Accudent.csv
    └── 2025-12_Report.pdf
```

### Re-running Files (Idempotent Updates)

If you process the same invoice twice:
- App identifies it by (Date Due, Patient Name, Total Cost)
- Updates existing row instead of creating duplicate
- Useful for:
  - Correcting errors
  - Adding new invoices to existing month
  - Regenerating reports with updated data

### Settings

Click "Settings…" to configure:

**Output Folder**
- Default: `~/Documents/AccudentLab/`
- Change to any folder you prefer
- Click "Browse…" to select

**CSV Mirror**
- ✓ Enabled (default): Creates both XLSX and CSV
- ☐ Disabled: XLSX only

**Month Override**
- Leave blank: Auto-detect from Due Date (recommended)
- Enter YYYY-MM: Force all invoices into specific month

## Viewing Results

### Excel File
```bash
open ~/Documents/AccudentLab/2025-10/2025-10_Accudent.xlsx
```

Or click **"Open This Month's Sheet"** in the app.

Columns:
- Date Due (m/d/yyyy format)
- Patient Name
- Total Units
- Unit Price (blank if mixed prices)
- Alloys/Extras Cost
- Total Cost

Sorted by Date Due, ascending.

### PDF Report
```bash
open ~/Documents/AccudentLab/2025-10/2025-10_Report.pdf
```

Or click **"Open Report PDF"** in the app.

Print-ready format with:
- All 6 columns in a table
- Footer totals
- Professional styling

### CSV File
```bash
cat ~/Documents/AccudentLab/2025-10/2025-10_Accudent.csv
```

Same data as XLSX, plain text format for importing elsewhere.

## Troubleshooting

### "Conversion failed" error
- **Cause:** Pages app not found or can't open .pages file
- **Solution:** Ensure Pages is installed. App will try fallback extraction.

### "No line items found" error
- **Cause:** Invoice table not detected
- **Solution:** Check invoice has header row with DESCRIPTION, QUANTITY, UNIT PRICE, COST

### "Could not find Patient:" error
- **Cause:** Footer pattern not found
- **Solution:** Ensure invoice has `Patient: {Name}, Due {m/d/yyyy}` footer

### App won't launch

**If you see `ModuleNotFoundError: No module named '_tkinter'` or tcl-tk errors:**
```bash
# Install Python 3.12 with tkinter
brew install python@3.12 python-tk@3.12

# Rebuild virtual environment
rm -rf venv
/opt/homebrew/bin/python3.12 -m venv venv
./venv/bin/pip install -r requirements.txt
```

**Other issues:**
```bash
# Check Python version (need 3.12)
/opt/homebrew/bin/python3.12 --version

# Reinstall dependencies
./venv/bin/pip install --force-reinstall -r requirements.txt

# Try running directly
./venv/bin/python accudent_app.py
```

### View logs
```bash
# Latest run log
ls -lt ~/Documents/AccudentLab/logs/*.log | head -1

# View it
tail -f ~/Documents/AccudentLab/logs/accudent_*.log
```

## Building macOS .app (Optional)

To create a standalone app you can double-click:

```bash
# Install pyinstaller
./venv/bin/pip install pyinstaller

# Build
./make_app.sh

# Result: dist/Accudent Importer.app

# Install to Applications
cp -r "dist/Accudent Importer.app" /Applications/

# Launch
open /Applications/Accudent\ Importer.app
```

## Next Steps

1. ✅ Test with sample invoice
2. ✅ Process real invoices
3. 📊 Open Excel sheet, verify data
4. 🖨️ Print or share the PDF report
5. 🔁 Re-run anytime to update

For detailed documentation, see:
- `README.md` - Full user guide
- `PROJECT_STRUCTURE.md` - Technical architecture
- `EXAMPLE_OUTPUT.md` - Output format examples
