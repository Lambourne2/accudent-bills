# ✅ Setup Complete!

Your Accudent Invoice Importer is now installed and running.

## What Was Fixed

**Issue:** `ModuleNotFoundError: No module named '_tkinter'`

**Solution:** Installed Python 3.12 with tkinter support (Python 3.13's tkinter had compatibility issues with the current tcl-tk version).

## Installation Summary

```bash
✓ brew install python@3.12 python-tk@3.12
✓ /opt/homebrew/bin/python3.12 -m venv venv
✓ ./venv/bin/pip install -r requirements.txt
✓ ./run.sh  # App is now running!
```

## Current Status

🟢 **App is running** - You should see a window titled "Accudent Importer"

## Next Steps

### 1. Test with Sample Invoice

Try processing the included sample:

1. In the app window, click the drop zone (or drag files onto it)
2. Select `Dr. Aldredge          mm.pages`
3. Wait for processing (should take ~5 seconds)
4. The report PDF will open automatically in Preview

Expected output location:
```
~/Documents/AccudentLab/2025-10/
├── 2025-10_Accudent.xlsx
├── 2025-10_Accudent.csv
└── 2025-10_Report.pdf
```

### 2. Process Your Invoices

- Drag and drop multiple .pages or .pdf files at once
- The app groups them by month automatically
- Re-running the same files updates existing data (no duplicates)

### 3. Open Results

After processing, use the buttons in the app:
- **"Open This Month's Sheet"** → Opens Excel file
- **"Open Report PDF"** → Opens the print-ready PDF

## Important Notes

### Python Version

This app **requires Python 3.12** (not 3.13) due to tkinter compatibility on your macOS version.

Always use:
```bash
/opt/homebrew/bin/python3.12 -m venv venv
```

### Running the App

Quick launch:
```bash
cd /Users/peytonlambourne/Code/accudent-bills
./run.sh
```

Or directly:
```bash
./venv/bin/python accudent_app.py
```

### If You Need to Reinstall

```bash
rm -rf venv
/opt/homebrew/bin/python3.12 -m venv venv
./venv/bin/pip install -r requirements.txt
./run.sh
```

## Documentation

- **QUICKSTART.md** - Step-by-step usage guide
- **README.md** - Full feature documentation
- **PROJECT_STRUCTURE.md** - Technical architecture
- **EXAMPLE_OUTPUT.md** - Output format examples

## Support

### View Logs

If something goes wrong:
```bash
ls -lt ~/Documents/AccudentLab/logs/*.log | head -1
tail -50 ~/Documents/AccudentLab/logs/accudent_*.log
```

### Test Parsing

Test a single invoice before processing:
```bash
./venv/bin/python test_parsing.py "path/to/invoice.pages"
```

### Common Issues

**App won't launch:**
- Ensure you're using Python 3.12: `/opt/homebrew/bin/python3.12 --version`
- Reinstall tkinter: `brew reinstall python-tk@3.12`

**Conversion fails:**
- Ensure Pages app is installed
- App will try to extract Preview.pdf from .pages package as fallback

**Parsing errors:**
- Check invoice has footer: `Patient: {Name}, Due {m/d/yyyy}`
- Check table has headers: DESCRIPTION | QUANTITY | UNIT PRICE | COST

## What the App Does

1. **Converts** .pages files to PDF (via AppleScript or extraction)
2. **Extracts** text from PDFs (using PyObjC PDFKit)
3. **Parses** patient name, date, units, pricing, and costs
4. **Writes** data to Excel (XLSX) with proper formatting
5. **Generates** CSV mirror (optional)
6. **Creates** print-ready PDF report with totals
7. **Organizes** by month in `~/Documents/AccudentLab/YYYY-MM/`

## Building macOS .app (Optional)

To create a double-clickable application:

```bash
./venv/bin/pip install pyinstaller
./make_app.sh

# Install to Applications
cp -r "dist/Accudent Importer.app" /Applications/
```

Then launch from Launchpad or Finder.

---

**You're all set!** 🎉

Start by processing the sample invoice, then add your own dental lab invoices.
