# OCRBulkProcessor

OCRBulkProcessor is a PySide6 application that simplifies running Tesseract OCR on many files at once. The graphical interface lets you add images or PDFs, pick an output folder, and process them in bulk. Results can be saved individually or merged together, depending on your preferences.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd OCRBulkProcessor
   ```
2. **Install Python dependencies**
   Install the required packages into your environment. Using a virtual environment is recommended:
   ```bash
   pip install PySide6 pytesseract pdf2image PyPDF2
   ```
3. **Install Tesseract OCR**
   Download the Tesseract program for your operating system and ensure the `tesseract` executable is available on your path.

## Tesseract path configuration

The default path to the Tesseract binary is set inside `ocr/engine.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
If Tesseract is installed elsewhere, edit this line to match your installation (for example `/usr/bin/tesseract` on Linux). You may also remove the line entirely if the command is already in your system path.

## Usage

Run the main application from the repository root:
```bash
python main.py
```
A window will appear where you can:
- Choose image or PDF files (or entire directories)
- Specify an output folder
- Enable subfolder scanning and concatenation
- Select the output format: plain text, HOCR HTML, or searchable PDF
- Monitor progress in the log area and progress bar

When processing completes, results are saved in the output folder. If concatenation is enabled, a single file with the name you provide will be created.

## Features

- Drag-and-drop support for quickly adding files
- Optional dark theme and persistent user settings
- PDF support through `pdf2image` and merging via `PyPDF2`

## Dependencies

- [PySide6](https://pypi.org/project/PySide6/) – GUI framework
- [pytesseract](https://pypi.org/project/pytesseract/) – Python bindings for Tesseract
- [pdf2image](https://pypi.org/project/pdf2image/) – convert PDF pages to images
- [PyPDF2](https://pypi.org/project/PyPDF2/) – optional merging for multi-page PDFs

Ensure these packages are installed before running the application.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
