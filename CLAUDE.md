# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OCR Bulk Processor is a PySide6-based GUI application that performs OCR on multiple images or PDFs using Tesseract. It supports bulk processing with options to output plain text, HOCR (HTML), or searchable PDF files. The application can concatenate results and merge multi-page PDFs.

## Running the Application

```bash
# Run the GUI application
python main.py

# Alternative entry point (legacy single-file version)
python ocr_tool.py
```

Note: There are two entry points:
- `main.py` - Uses the modular structure (gui/, ocr/, config/, resources/)
- `ocr_tool.py` - Legacy single-file implementation with all functionality in one file

## Architecture

### Module Structure

The codebase follows a modular architecture with clear separation of concerns:

- **gui/** - Qt GUI components
  - `main_window.py` - Main application window, handles UI layout, user interaction, drag-and-drop, and settings persistence via QSettings
  - `worker.py` - OCRWorker QThread for background OCR processing, manages file processing loop and concatenation logic

- **ocr/** - OCR processing logic
  - `engine.py` - Core OCR function using pytesseract, handles text/HOCR/PDF output formats
  - `pdf_utils.py` - PDF-related utilities with graceful fallback if pdf2image or PyPDF2 not installed

- **config/** - Application configuration
  - `settings.py` - QSettings factory function for persistent app settings

- **resources/** - UI resources
  - `theme.py` - Dark theme stylesheet and theme application logic

### Key Design Patterns

**Multi-threaded Processing**: OCR operations run in a background QThread (OCRWorker) to prevent UI freezing. Progress updates are sent via Qt Signals to the main window.

**Settings Persistence**: Uses QSettings to remember user preferences (last input/output folders, theme choice, concatenation settings) across application restarts.

**Optional Dependencies**: The application gracefully handles missing PDF dependencies:
- `PDF_SUPPORT` flag indicates if pdf2image is available for PDF-to-image conversion
- `PDF_MERGE_SUPPORT` flag indicates if PyPDF2 is available for multi-page PDF merging
- If missing, relevant features are disabled with user warnings

**File Delimiter**: Multiple input files are stored as pipe-delimited strings ("|") in the UI text field.

## Dependencies

### Required
- PySide6 - Qt framework for GUI
- pytesseract - Python wrapper for Tesseract OCR
- Pillow (PIL) - Image processing
- Tesseract-OCR - Must be installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` (hardcoded path in ocr/engine.py:5)

### Optional
- pdf2image - Required for PDF input file support
- PyPDF2 - Required for merging multiple single-page PDFs into one multi-page PDF

## Important Implementation Details

### Tesseract Path Configuration
The Tesseract executable path is hardcoded in `ocr/engine.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```
This path may need adjustment for different environments.

### OCR Configuration
The OCR engine uses specific Tesseract parameters:
- `--oem 3` - LSTM OCR Engine Mode
- `--psm 3` - Automatic page segmentation
- `-c preserve_interword_spaces=1` - Preserve spacing between words

### PDF Processing Workflow
1. Input PDFs are converted to PNG images via pdf2image (saved to output directory)
2. Each PNG is processed through OCR
3. If concatenating PDFs, single-page PDFs are stored in temp directory
4. PyPDF2 merges all single-page PDFs into final output

### HOCR Concatenation Limitation
When concatenating HOCR output, only the last processed page is written to the final file (not a true merge). This is a known limitation mentioned in worker.py:80.

### Theme System
Three themes are supported: Light, Dark, System. The theme preference is saved to QSettings and reapplied on startup. Theme changes are applied by setting/clearing the application stylesheet.
