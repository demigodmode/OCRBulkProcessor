from PySide6.QtCore import QThread, Signal
import os
import tempfile

from ocr.engine import ocr_preserve_format
from ocr.pdf_utils import PDF_MERGE_SUPPORT, merge_pdfs
from PyPDF2 import PdfMerger  # used only if PDF_MERGE_SUPPORT is True


class OCRWorker(QThread):
    """
    Background worker for OCR tasks. Creates single-page outputs,
    then merges them if needed (for PDF).
    """
    progress_signal = Signal(str)      # log messages to the GUI
    done_signal = Signal()             # emitted when all tasks complete
    progress_bar_signal = Signal(int)  # used to update progress bar

    def __init__(self, file_list, output_dir, concatenate,
                 output_format, concat_filename):
        super().__init__()
        self.file_list = file_list
        self.output_dir = output_dir
        self.concatenate = concatenate
        self.output_format = output_format  # "txt", "hocr", or "pdf"
        self.concat_filename = concat_filename
        self.cancelled = False

    def run(self):
        total_files = len(self.file_list)
        if total_files == 0:
            self.done_signal.emit()
            return

        # For text-based concatenation
        text_buffer = []
        # For HOCR/PDF concatenation
        binary_buffer = []

        # If we need to do PDF merging, store single-page PDFs in a temp folder
        single_page_pdfs = []

        for i, path in enumerate(self.file_list):
            if self.cancelled:
                break

            filename = os.path.basename(path)
            self.progress_bar_signal.emit(int((i + 1) / total_files * 100))
            self.progress_signal.emit(f"Extracting from {filename}...")

            try:
                result = ocr_preserve_format(path, self.output_format)
            except Exception as e:
                self.progress_signal.emit(f"ERROR on {filename}: {e}")
                continue

            self.progress_signal.emit("OCR done.")

            # If not concatenating:
            if not self.concatenate:
                base_name, _ = os.path.splitext(filename)
                if self.output_format == "txt":
                    out_path = os.path.join(self.output_dir, base_name + ".txt")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(result)
                elif self.output_format == "hocr":
                    out_path = os.path.join(self.output_dir, base_name + ".hocr")
                    with open(out_path, "wb") as f:
                        f.write(result)
                else:
                    # single-page PDF
                    out_path = os.path.join(self.output_dir, base_name + "_ocr.pdf")
                    with open(out_path, "wb") as f:
                        f.write(result)
            else:
                # If concatenating
                if self.output_format == "txt":
                    text_buffer.append(f"--- OCR from {filename} ---\n{result}\n")
                elif self.output_format == "hocr":
                    # HOCR is tricky to merge. We'll store each page, then write the last one.
                    binary_buffer.append(result)
                else:
                    # PDF => produce a single-page PDF in a temp folder
                    temp_dir = tempfile.gettempdir()
                    single_page_path = os.path.join(temp_dir, f"__ocr_tmp_{i}.pdf")
                    with open(single_page_path, "wb") as f:
                        f.write(result)
                    single_page_pdfs.append(single_page_path)

        self.progress_bar_signal.emit(100)

        if self.concatenate:
            final_path = os.path.join(self.output_dir, self.concat_filename)
            if self.output_format == "txt":
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(text_buffer))
                self.progress_signal.emit(f"All text combined into: {final_path}")

            elif self.output_format == "hocr":
                # We only write the last HOCR page
                if binary_buffer:
                    with open(final_path, "wb") as f:
                        f.write(binary_buffer[-1])
                    self.progress_signal.emit(
                        f"(HOCR) Wrote only the last page to: {final_path}"
                    )

            else:
                # PDF merging
                if not PDF_MERGE_SUPPORT:
                    # If PyPDF2 isn't installed, we can only write the last PDF
                    if single_page_pdfs:
                        last_pdf = single_page_pdfs[-1]
                        with open(final_path, "wb") as fout, open(last_pdf, "rb") as fin:
                            fout.write(fin.read())
                        self.progress_signal.emit(
                            f"No PyPDF2 installed. Wrote last PDF only -> {final_path}"
                        )
                else:
                    # Merge single-page PDFs
                    merger = PdfMerger()
                    for pdf_page in single_page_pdfs:
                        merger.append(pdf_page)
                    try:
                        merger.write(final_path)
                        merger.close()
                        self.progress_signal.emit(f"Merged multi-page PDF -> {final_path}")
                    except Exception as e:
                        self.progress_signal.emit(f"PDF merge error: {e}")

        self.done_signal.emit()
