#!/usr/bin/env python3
"""
Accudent Lab Invoice Importer
Main GUI application with drag-and-drop support.
"""

import logging
import os
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional

from converter import ensure_pdf
from extractor import extract_text
from parser import parse_invoice
from writer import get_month_folder, write_xlsx, write_csv, load_existing_rows
from report_generator import build_report_pdf, open_pdf_in_preview


class AccudentApp:
    """Main application window."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Accudent Importer")
        self.root.geometry("600x500")
        
        # Settings
        self.output_folder = tk.StringVar(value=os.path.expanduser("~/Documents/AccudentLab"))
        self.csv_mirror_enabled = tk.BooleanVar(value=True)
        self.month_override = tk.StringVar(value="")  # Empty = auto-detect
        self.dentist_name_override = tk.StringVar(value='')  # Empty = auto-detect
        
        # State
        self.processing = False
        self.current_month_folder = None
        self.exceptions = []  # List of (filepath, error_msg, parsed_data_dict)
        
        # Setup logging
        self._setup_logging()
        
        # Build UI
        self._build_ui()
        
        # Enable drag-and-drop
        self._setup_drag_drop()
    
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_folder = Path(self.output_folder.get()) / 'logs'
        log_folder.mkdir(parents=True, exist_ok=True)
        
        log_file = log_folder / f"accudent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _build_ui(self):
        """Build the main UI."""
        # Header
        header = tk.Label(
            self.root,
            text="📄 Accudent Invoice Importer",
            font=("Helvetica", 18, "bold"),
            pady=20
        )
        header.pack()
        
        # Drop zone
        drop_frame = tk.Frame(self.root, bg="#e8f4f8", relief=tk.RIDGE, borderwidth=3)
        drop_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        self.drop_label = tk.Label(
            drop_frame,
            text="Drop .pages or .pdf invoices here\n\n(or click to select files)",
            font=("Helvetica", 14),
            bg="#e8f4f8",
            fg="#555",
            cursor="hand2"
        )
        self.drop_label.pack(expand=True)
        self.drop_label.bind("<Button-1>", lambda e: self._browse_files())
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, padx=40, fill=tk.X)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Helvetica", 11),
            fg="#333"
        )
        self.status_label.pack(pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        self.btn_open_sheet = tk.Button(
            button_frame,
            text="Open This Month's Sheet",
            command=self._open_current_sheet,
            state=tk.DISABLED,
            width=22
        )
        self.btn_open_sheet.grid(row=0, column=0, padx=5)
        
        self.btn_open_report = tk.Button(
            button_frame,
            text="Open Report PDF",
            command=self._open_current_report,
            state=tk.DISABLED,
            width=22
        )
        self.btn_open_report.grid(row=0, column=1, padx=5)
        
        self.btn_settings = tk.Button(
            button_frame,
            text="Settings…",
            command=self._show_settings,
            width=22
        )
        self.btn_settings.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_exceptions = tk.Button(
            button_frame,
            text="Review Exceptions (0)",
            command=self._show_exceptions,
            state=tk.DISABLED,
            width=22
        )
        self.btn_exceptions.grid(row=1, column=1, padx=5, pady=5)
        
        self.btn_reset = tk.Button(
            button_frame,
            text="Reset This Month's Sheet",
            command=self._reset_current_month,
            state=tk.DISABLED,
            width=22,
            fg="red"
        )
        self.btn_reset.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    
    def _setup_drag_drop(self):
        """Setup drag-and-drop on macOS using tkinterdnd2 or basic binding."""
        # Try tkinterdnd2 if available, otherwise use basic file open
        # For simplicity, we'll use click-to-browse for now
        # Full drag-drop requires tkinterdnd2 which is optional
        pass
    
    def _browse_files(self):
        """Open file browser to select invoice files."""
        if self.processing:
            return
        
        files = filedialog.askopenfilenames(
            title="Select Invoice Files",
            filetypes=[
                ("Invoice Files", "*.pages *.pdf"),
                ("Pages Files", "*.pages"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )
        
        if files:
            self._process_files(list(files))
    
    def _process_files(self, file_paths: List[str]):
        """
        Process dropped or selected files in background thread.
        
        Args:
            file_paths: List of file paths to process
        """
        if self.processing:
            messagebox.showwarning("Busy", "Already processing files. Please wait.")
            return
        
        self.processing = True
        self.exceptions = []
        
        # Start processing in background
        thread = threading.Thread(target=self._process_files_worker, args=(file_paths,))
        thread.daemon = True
        thread.start()
        
        # Start progress animation
        self.progress.start(10)
        self.status_label.config(text=f"Processing {len(file_paths)} file(s)…")
    
    def _process_files_worker(self, file_paths: List[str]):
        """Worker thread for processing files."""
        try:
            self.logger.info(f"Processing {len(file_paths)} files")
            
            # Group by month
            months_data = {}  # {month_folder_path: [row_dicts]}
            
            for i, file_path in enumerate(file_paths, 1):
                self._update_status(f"[{i}/{len(file_paths)}] Converting {Path(file_path).name}…")
                
                pdf_to_cleanup = None
                try:
                    # Convert to PDF if needed
                    original_path = Path(file_path)
                    pdf_path = ensure_pdf(file_path)
                    
                    # Mark PDF for cleanup if we converted from .pages
                    if original_path.suffix.lower() == '.pages' and pdf_path != file_path:
                        pdf_to_cleanup = pdf_path
                    
                    self._update_status(f"[{i}/{len(file_paths)}] Extracting text…")
                    
                    # Extract text
                    text = extract_text(pdf_path)
                    
                    self._update_status(f"[{i}/{len(file_paths)}] Parsing invoice…")
                    
                    # Parse invoice
                    parsed_data = parse_invoice(text)
                    
                    # Determine month folder
                    month_folder = get_month_folder(
                        parsed_data['date_due'],
                        self.output_folder.get()
                    )
                    
                    # Add to month's data
                    if month_folder not in months_data:
                        months_data[month_folder] = []
                    
                    months_data[month_folder].append(parsed_data)
                    
                    self.logger.info(f"Parsed {file_path}: {parsed_data['patient_name']}, ${parsed_data['total_cost']}")
                    
                    # Clean up intermediate PDF if it was converted from .pages
                    if pdf_to_cleanup and Path(pdf_to_cleanup).exists():
                        Path(pdf_to_cleanup).unlink()
                        self.logger.info(f"Cleaned up intermediate PDF: {pdf_to_cleanup}")
                
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    self.exceptions.append((file_path, str(e), None))
                    # Clean up PDF even on error
                    if pdf_to_cleanup and Path(pdf_to_cleanup).exists():
                        try:
                            Path(pdf_to_cleanup).unlink()
                        except:
                            pass
            
            # Prompt for dentist name confirmation if we have data
            if months_data:
                # Get the auto-detected dentist name from first row of first month
                first_month_rows = list(months_data.values())[0]
                detected_name = first_month_rows[0].get('dentist_name', '') if first_month_rows else ''
                
                # Show confirmation dialog (run in main thread)
                confirmed_name = self._prompt_dentist_name(detected_name)
                
                # Apply confirmed name to all rows
                if confirmed_name:
                    for month_rows in months_data.values():
                        for row in month_rows:
                            row['dentist_name'] = confirmed_name
            
            # Write to files for each month
            for month_folder, rows in months_data.items():
                self._update_status(f"Writing to {month_folder.name}…")
                
                # Load existing rows
                existing_rows = load_existing_rows(month_folder)
                
                # Merge: new rows + existing rows
                all_rows = existing_rows + rows
                
                # Write XLSX
                xlsx_path = write_xlsx(month_folder, all_rows)
                self.logger.info(f"Wrote XLSX: {xlsx_path}")
                
                # Write CSV if enabled
                if self.csv_mirror_enabled.get():
                    csv_path = write_csv(month_folder, all_rows)
                    self.logger.info(f"Wrote CSV: {csv_path}")
                
                # Build report PDF
                self._update_status(f"Building report for {month_folder.name}…")
                pdf_path = build_report_pdf(month_folder, all_rows)
                self.logger.info(f"Built report PDF: {pdf_path}")
                
                # Store current month for buttons
                self.current_month_folder = month_folder
            
            # Done
            self._finish_processing(success=True)
        
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            self._finish_processing(success=False, error=str(e))
    
    def _update_status(self, message: str):
        """Update status label (thread-safe)."""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def _finish_processing(self, success: bool, error: str = None):
        """Called when processing completes."""
        self.root.after(0, self._finish_processing_ui, success, error)
    
    def _finish_processing_ui(self, success: bool, error: str = None):
        """UI updates when processing completes."""
        self.processing = False
        self.progress.stop()
        
        if success:
            exc_count = len(self.exceptions)
            if exc_count > 0:
                self.status_label.config(
                    text=f"✓ Done with {exc_count} exception(s)",
                    fg="orange"
                )
                self.btn_exceptions.config(
                    text=f"Review Exceptions ({exc_count})",
                    state=tk.NORMAL
                )
            else:
                self.status_label.config(text="✓ All files processed successfully", fg="green")
            
            # Enable buttons
            self.btn_open_sheet.config(state=tk.NORMAL)
            self.btn_open_report.config(state=tk.NORMAL)
            self.btn_reset.config(state=tk.NORMAL)
            
            # Auto-open report if single month
            if self.current_month_folder:
                self._open_current_report()
        else:
            self.status_label.config(text=f"✗ Error: {error}", fg="red")
            messagebox.showerror("Processing Error", error)
    
    def _open_current_sheet(self):
        """Open current month's XLSX file."""
        if not self.current_month_folder:
            messagebox.showwarning("No Data", "No monthly sheet available yet.")
            return
        
        xlsx_path = self.current_month_folder / f"{self.current_month_folder.name}_Accudent.xlsx"
        
        if xlsx_path.exists():
            subprocess.run(['open', str(xlsx_path)])
        else:
            messagebox.showwarning("Not Found", f"Sheet not found: {xlsx_path}")
    
    def _open_current_report(self):
        """Open current month's report PDF."""
        if not self.current_month_folder:
            messagebox.showwarning("No Data", "No report available yet.")
            return
        
        pdf_path = self.current_month_folder / f"{self.current_month_folder.name}_Report.pdf"
        
        if pdf_path.exists():
            open_pdf_in_preview(pdf_path)
        else:
            messagebox.showwarning("Not Found", f"Report not found: {pdf_path}")
    
    def _show_settings(self):
        """Show settings dialog."""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("500x330")
        
        # Output folder
        tk.Label(settings_win, text="Output Folder:", font=("Helvetica", 11)).grid(
            row=0, column=0, sticky=tk.W, padx=20, pady=10
        )
        
        folder_frame = tk.Frame(settings_win)
        folder_frame.grid(row=0, column=1, sticky=tk.EW, padx=20, pady=10)
        
        folder_entry = tk.Entry(folder_frame, textvariable=self.output_folder, width=30)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            folder_frame,
            text="Browse…",
            command=lambda: self._browse_folder()
        ).pack(side=tk.LEFT, padx=5)
        
        # CSV mirror
        tk.Checkbutton(
            settings_win,
            text="Generate CSV mirror",
            variable=self.csv_mirror_enabled,
            font=("Helvetica", 11)
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=20, pady=10)
        
        # Month override
        tk.Label(settings_win, text="Month Override:", font=("Helvetica", 11)).grid(
            row=2, column=0, sticky=tk.W, padx=20, pady=10
        )
        tk.Label(
            settings_win,
            text="(Leave blank to auto-detect from Due Date)",
            font=("Helvetica", 9),
            fg="gray"
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=20)
        
        month_entry = tk.Entry(settings_win, textvariable=self.month_override, width=15)
        month_entry.grid(row=2, column=1, sticky=tk.W, padx=20, pady=10)
        
        # Dentist name override
        tk.Label(settings_win, text="Dentist Name:", font=("Helvetica", 11)).grid(
            row=4, column=0, sticky=tk.W, padx=20, pady=10
        )
        tk.Label(
            settings_win,
            text="(Leave blank to auto-detect from invoice)",
            font=("Helvetica", 9),
            fg="gray"
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=20)
        
        dentist_entry = tk.Entry(settings_win, textvariable=self.dentist_name_override, width=30)
        dentist_entry.grid(row=4, column=1, sticky=tk.W, padx=20, pady=10)
        
        # Close button
        tk.Button(
            settings_win,
            text="Close",
            command=settings_win.destroy,
            width=15
        ).grid(row=6, column=0, columnspan=2, pady=20)
    
    def _prompt_dentist_name(self, detected_name: str) -> str:
        """
        Prompt user to confirm or edit dentist name.
        Runs in main thread via queue.
        
        Args:
            detected_name: Auto-detected name from invoice
            
        Returns:
            Confirmed dentist name
        """
        import queue
        result_queue = queue.Queue()
        
        def show_dialog():
            # Check if there's an override in settings first
            if self.dentist_name_override.get().strip():
                result_queue.put(self.dentist_name_override.get().strip())
                return
            
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Confirm Dentist Name")
            dialog.geometry("450x180")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Message
            tk.Label(
                dialog,
                text="Please confirm or edit the dentist name for the report:",
                font=("Helvetica", 11),
                wraplength=400
            ).pack(pady=15)
            
            # Entry field
            name_var = tk.StringVar(value=detected_name)
            entry = tk.Entry(dialog, textvariable=name_var, font=("Helvetica", 12), width=35)
            entry.pack(pady=10)
            entry.focus_set()
            entry.select_range(0, tk.END)
            
            # Buttons
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=15)
            
            def on_confirm():
                result_queue.put(name_var.get().strip())
                dialog.destroy()
            
            def on_cancel():
                result_queue.put(detected_name)  # Use detected name if cancelled
                dialog.destroy()
            
            tk.Button(
                button_frame,
                text="Confirm",
                command=on_confirm,
                width=12,
                font=("Helvetica", 10)
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame,
                text="Use As-Is",
                command=on_cancel,
                width=12,
                font=("Helvetica", 10)
            ).pack(side=tk.LEFT, padx=5)
            
            # Handle Enter key
            entry.bind('<Return>', lambda e: on_confirm())
            
            dialog.wait_window()
        
        # Run dialog in main thread
        self.root.after(0, show_dialog)
        
        # Wait for result
        return result_queue.get()
    
    def _browse_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_folder.get()
        )
        if folder:
            self.output_folder.set(folder)
    
    def _reset_current_month(self):
        """Reset/delete the current month's sheet files."""
        if not self.current_month_folder:
            messagebox.showwarning("No Data", "No monthly data to reset.")
            return
        
        month_name = self.current_month_folder.name
        
        # Confirm with user
        confirm = messagebox.askyesno(
            "Reset Month",
            f"Are you sure you want to delete all files for {month_name}?\n\n"
            "This will permanently delete:\n"
            f"• {month_name}_Accudent.xlsx\n"
            f"• {month_name}_Accudent.csv\n"
            f"• {month_name}_Report.pdf\n\n"
            "This action cannot be undone.",
            icon='warning'
        )
        
        if not confirm:
            return
        
        try:
            # Delete the files
            xlsx_path = self.current_month_folder / f"{month_name}_Accudent.xlsx"
            csv_path = self.current_month_folder / f"{month_name}_Accudent.csv"
            pdf_path = self.current_month_folder / f"{month_name}_Report.pdf"
            
            deleted = []
            for file_path in [xlsx_path, csv_path, pdf_path]:
                if file_path.exists():
                    file_path.unlink()
                    deleted.append(file_path.name)
                    self.logger.info(f"Deleted {file_path}")
            
            if deleted:
                messagebox.showinfo(
                    "Reset Complete",
                    f"Successfully deleted {len(deleted)} file(s) for {month_name}:\n\n" +
                    "\n".join(f"• {name}" for name in deleted)
                )
                
                # Disable buttons since no data exists
                self.btn_open_sheet.config(state=tk.DISABLED)
                self.btn_open_report.config(state=tk.DISABLED)
                self.btn_reset.config(state=tk.DISABLED)
                self.current_month_folder = None
                self.status_label.config(text="Month reset - ready to process new files")
            else:
                messagebox.showinfo("Nothing to Delete", f"No files found for {month_name}.")
        
        except Exception as e:
            self.logger.error(f"Failed to reset month: {e}", exc_info=True)
            messagebox.showerror("Reset Failed", f"Failed to delete files: {e}")
    
    def _show_exceptions(self):
        """Show exceptions panel for manual review."""
        if not self.exceptions:
            messagebox.showinfo("No Exceptions", "No exceptions to review.")
            return
        
        exc_win = tk.Toplevel(self.root)
        exc_win.title(f"Exceptions ({len(self.exceptions)})")
        exc_win.geometry("700x500")
        
        # List of exceptions
        tk.Label(
            exc_win,
            text="Files needing manual confirmation:",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(exc_win)
        scrollbar = ttk.Scrollbar(exc_win, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add exceptions
        for i, (filepath, error, parsed_data) in enumerate(self.exceptions):
            frame = tk.LabelFrame(
                scrollable_frame,
                text=Path(filepath).name,
                font=("Helvetica", 10, "bold"),
                padx=10,
                pady=10
            )
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(
                frame,
                text=f"Error: {error}",
                fg="red",
                wraplength=600
            ).pack(anchor=tk.W)
            
            # TODO: Add inline edit fields for manual correction
            # For now, just show the error
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        tk.Button(
            exc_win,
            text="Close",
            command=exc_win.destroy,
            width=15
        ).pack(pady=10)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = AccudentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
