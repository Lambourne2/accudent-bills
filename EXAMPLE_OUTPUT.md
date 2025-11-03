# Example Output Structure

When you process invoices, the app creates a folder structure like this:

```
~/Documents/AccudentLab/
├── 2025-10/
│   ├── 2025-10_Accudent.xlsx       # Primary Excel spreadsheet
│   ├── 2025-10_Accudent.csv        # CSV mirror (if enabled)
│   ├── 2025-10_Report.pdf          # Print-ready monthly report
│   └── logs/
│       └── accudent_20251025_143022.log
├── 2025-11/
│   ├── 2025-11_Accudent.xlsx
│   ├── 2025-11_Accudent.csv
│   ├── 2025-11_Report.pdf
│   └── logs/
│       └── accudent_20251102_091545.log
└── logs/
    └── accudent_20251102_163045.log
```

## Excel File (XLSX)

**Sheet Name:** `Accudent`

**Columns:**

| Date Due  | Patient Name  | Total Units | Unit Price | Alloys/Extras Cost | Total Cost |
|-----------|---------------|-------------|------------|-------------------|-----------|
| 10/7/2025 | Marcia Miller | 1           | $100.00    | $0.00             | $100.00   |
| 10/15/2025| John Smith    | 3           | $85.00     | $45.00            | $300.00   |
| 10/22/2025| Jane Doe      | 2           |            | $0.00             | $200.00   |

**Notes:**
- Dates are formatted as `m/d/yyyy`
- Unit Price is blank if multiple different prices exist in the invoice
- Numbers are formatted as currency: `$#,##0.00`
- Rows are sorted by Date Due (ascending)
- Hidden column G contains formula: `=IF(C2*(D2+E2)=0,"",C2*(D2+E2))` for legacy compatibility

## CSV File

Same data as XLSX, but in plain CSV format (columns A-F only, no hidden column):

```csv
Date Due,Patient Name,Total Units,Unit Price,Alloys/Extras Cost,Total Cost
10/7/2025,Marcia Miller,1,$100.00,$0.00,$100.00
10/15/2025,John Smith,3,$85.00,$45.00,$300.00
10/22/2025,Jane Doe,2,,$0.00,$200.00
```

## PDF Report

Professional print-ready report with:

**Header:**
```
Accudent Dental Lab — October 2025
```

**Table:** Same columns as the spreadsheet, formatted for printing

**Footer Totals:**
```
Total Patients: 3
Total Units: 6
Total Cost: $600.00
Alloys/Extras: $45.00
```

The PDF automatically opens in Preview after generation.

## Log Files

Each run creates a timestamped log file:

```
2025-11-02 16:30:45,123 - INFO - Processing 10 files
2025-11-02 16:30:47,456 - INFO - Parsed Dr. Aldredge.pages: Marcia Miller, $100.00
2025-11-02 16:30:48,789 - INFO - Wrote XLSX: ~/Documents/AccudentLab/2025-10/2025-10_Accudent.xlsx
2025-11-02 16:30:49,012 - INFO - Built report PDF: ~/Documents/AccudentLab/2025-10/2025-10_Report.pdf
```

Use logs for debugging if any invoices fail to process.
