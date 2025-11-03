# 📄 OCR Bulk Processor

> A powerful and user-friendly desktop application for batch OCR processing of images and PDFs with support for multiple output formats.

## ✨ Features

- **🖼️ Multi-Format Support** - Process PNG, JPG, JPEG, BMP, GIF, TIFF, and PDF files
- **📦 Batch Processing** - Handle multiple files at once with recursive subfolder scanning
- **🔄 Multiple Output Formats**
  - Plain Text (.txt)
  - HOCR/HTML (.hocr) - Preserves layout information
  - Searchable PDF (.pdf) - OCR text embedded in PDF format
- **📑 File Concatenation** - Merge results from multiple files into a single output
- **🎨 Theme Support** - Choose between Light, Dark, or System themes
- **🖱️ Drag & Drop** - Intuitive file selection via drag and drop
- **⚡ Background Processing** - Non-blocking UI with progress tracking
- **💾 Settings Persistence** - Remembers your preferences between sessions
- **🔧 Configurable Defaults** - Set default input and output folders

## 🚀 Getting Started

### Prerequisites

**Required:**
- Python 3.8 or higher
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - Windows: Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

**Python Dependencies:**
```bash
pip install PySide6 pytesseract Pillow
```

**Optional (for enhanced PDF support):**
```bash
pip install pdf2image PyPDF2
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/OCRBulkProcessor.git
   cd OCRBulkProcessor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install PySide6 pytesseract Pillow pdf2image PyPDF2
   ```

3. **Verify Tesseract installation**
   ```bash
   tesseract --version
   ```

4. **Configure Tesseract path** (if needed)

   Edit `ocr/engine.py` line 5 to match your Tesseract installation path:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

### Running the Application

```bash
python main.py
```

## 📖 Usage Guide

### Basic Workflow

1. **Select Input Files**
   - Click "Browse..." next to Images field
   - Or drag and drop files directly onto the window
   - Check "Include Subfolders" to process nested directories

2. **Choose Output Location**
   - Click "Browse..." next to Output field
   - Or set a default output folder in Preferences menu

3. **Configure Output Settings**
   - Select output format: Plain Text, HOCR, or Searchable PDF
   - Enable "Concatenate" to merge all results into a single file
   - Customize the concatenated filename if needed

4. **Process Files**
   - Click the green "Run OCR" button
   - Monitor progress in the log area
   - Processing happens in the background without freezing the UI

### Advanced Features

#### Setting Default Folders
Navigate to **Preferences** → **Set Default Input/Output Folder** to configure folders that auto-populate when starting the application.

#### Theme Customization
Switch themes via **Preferences** → **Theme** → Select Light, Dark, or System.

#### PDF Processing
- **Input PDFs**: Automatically converted to images before OCR (requires pdf2image)
- **Output PDFs**: Create searchable PDFs with embedded OCR text
- **Multi-page PDF Output**: Merge multiple single-page results into one PDF (requires PyPDF2)

## 🏗️ Project Structure

```
OCRBulkProcessor/
├── main.py                 # Application entry point
├── ocr_tool.py            # Legacy single-file version
├── gui/
│   ├── main_window.py     # Main application window and UI logic
│   └── worker.py          # Background OCR processing thread
├── ocr/
│   ├── engine.py          # Core OCR functionality
│   └── pdf_utils.py       # PDF conversion and merging utilities
├── config/
│   └── settings.py        # Application settings management
├── resources/
│   └── theme.py           # UI theme definitions
├── CLAUDE.md              # AI assistant development guide
└── README.md              # This file
```

## ⚙️ Configuration

### OCR Engine Settings

The application uses Tesseract with the following default parameters:
- **OEM 3**: LSTM OCR Engine Mode (best accuracy)
- **PSM 3**: Automatic page segmentation
- **preserve_interword_spaces=1**: Maintains spacing between words

These can be modified in `ocr/engine.py` in the `ocr_preserve_format()` function.

### Supported File Formats

**Input:** `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.tif`, `.tiff`, `.pdf`
**Output:** `.txt`, `.hocr`, `.pdf`

## 🔧 Troubleshooting

### Tesseract Not Found
**Error:** `TesseractNotFoundError`
**Solution:** Ensure Tesseract is installed and the path in `ocr/engine.py` is correct.

### PDF Processing Not Working
**Error:** "PDF support not installed"
**Solution:** Install pdf2image: `pip install pdf2image`
**Note:** On Windows, pdf2image also requires poppler. Download from [here](https://github.com/oschwartz10612/poppler-windows/releases/).

### PDF Merging Failed
**Error:** "No PyPDF2 installed"
**Solution:** Install PyPDF2: `pip install PyPDF2`

### Memory Issues with Large Files
**Solution:** Process files in smaller batches or reduce image resolution before OCR.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

© 2025 by DemiGodMode. All rights reserved.

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - The OCR engine powering this application
- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python framework
- [pytesseract](https://github.com/madmaze/pytesseract) - Python wrapper for Tesseract

## 📊 Version History

- **v2.3** (April 2025) - Modular architecture refactor, improved error handling
- **v2.2** (March 2025) - Added theme support and concatenation features
- **v2.0** - Initial multi-format support with GUI

---

<div align="center">
Made with ❤️ for efficient document processing
</div>
