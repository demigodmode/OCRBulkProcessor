import pytesseract
from PIL import Image

# Point to Tesseract installation:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ocr_preserve_format(image_path: str, output_format: str = "txt"):
    """
    Performs OCR on a single image, optionally producing HOCR or PDF.
    Return:
      - if "txt": a string
      - if "pdf"/"hocr": bytes
    """
    config = r"--oem 3 --psm 3 -c preserve_interword_spaces=1"

    if output_format == "txt":
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img, config=config)
    else:
        # HOCR or PDF
        extension = "pdf" if output_format == "pdf" else "hocr"
        with Image.open(image_path) as img:
            return pytesseract.image_to_pdf_or_hocr(img, extension=extension, config=config)
