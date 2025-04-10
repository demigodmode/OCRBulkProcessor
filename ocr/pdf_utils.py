# ocr/pdf_utils.py

try:
    from pdf2image import convert_from_path as _pdf2image_convert
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from PyPDF2 import PdfMerger
    PDF_MERGE_SUPPORT = True
except ImportError:
    PDF_MERGE_SUPPORT = False


def convert_from_path(pdf_path):
    """
    Wrapper for pdf2image.convert_from_path.
    Raises an error if pdf2image is not installed.
    """
    if not PDF_SUPPORT:
        raise RuntimeError("pdf2image is not installed; cannot convert PDFs.")
    return _pdf2image_convert(pdf_path)


def merge_pdfs(pdf_paths, output_path):
    """
    Merges single-page PDFs into a single multi-page PDF, if PDF_MERGE_SUPPORT is True.
    """
    if not PDF_MERGE_SUPPORT:
        raise RuntimeError("PyPDF2 is not installed; cannot merge PDFs.")

    merger = PdfMerger()
    for pdf_page in pdf_paths:
        merger.append(pdf_page)
    merger.write(output_path)
    merger.close()
