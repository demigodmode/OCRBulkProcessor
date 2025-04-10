import os
import tempfile
from pathlib import Path

from PySide6.QtCore import (
    Qt, QSettings, QThread, Signal
)
from PySide6.QtGui import (
    QAction, QDragEnterEvent, QDropEvent
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QMenuBar,
    QPlainTextEdit, QProgressBar, QComboBox
)

from gui.worker import OCRWorker
from ocr.pdf_utils import PDF_SUPPORT, convert_from_path
from config.settings import (
    create_qsettings
)
from resources.theme import (
    DARK_THEME_QSS, apply_theme
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Bulk Processor")
        self.setMinimumSize(800, 600)

        # Initialize QSettings
        self.settings = create_qsettings()

        # Central layout
        cw = QWidget()
        self.setCentralWidget(cw)
        main_layout = QVBoxLayout()
        cw.setLayout(main_layout)

        # Row 1: input
        row_in = QHBoxLayout()
        lbl_in = QLabel("Images:")
        lbl_in.setToolTip("Select image/PDF files for OCR.")
        self.txt_input = QLineEdit()
        btn_in = QPushButton("Browse...")
        btn_in.clicked.connect(self.browse_files)
        row_in.addWidget(lbl_in)
        row_in.addWidget(self.txt_input)
        row_in.addWidget(btn_in)
        main_layout.addLayout(row_in)

        # Row 2: output folder
        row_out = QHBoxLayout()
        lbl_out = QLabel("Output:")
        lbl_out.setToolTip("Select the folder where OCR results will be saved.")
        self.txt_output = QLineEdit()
        btn_out = QPushButton("Browse...")
        btn_out.clicked.connect(self.browse_output_dir)
        row_out.addWidget(lbl_out)
        row_out.addWidget(self.txt_output)
        row_out.addWidget(btn_out)
        main_layout.addLayout(row_out)

        # Row 3: subfolders + drag
        row_opts = QHBoxLayout()
        self.chk_subfolders = QCheckBox("Include Subfolders")
        self.chk_concatenate = QCheckBox("Concatenate")
        row_opts.addWidget(self.chk_subfolders)
        row_opts.addWidget(self.chk_concatenate)
        main_layout.addLayout(row_opts)

        # Row 4: format + concat name
        row_fmt = QHBoxLayout()
        lbl_fmt = QLabel("Output Format:")
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(["Plain Text", "HOCR (HTML)", "Searchable PDF"])
        self.cmb_format.currentIndexChanged.connect(self.on_format_change)

        lbl_concat = QLabel("Concatenated File Name:")
        self.txt_concat_file = QLineEdit("all_ocr_results.txt")

        row_fmt.addWidget(lbl_fmt)
        row_fmt.addWidget(self.cmb_format)
        row_fmt.addWidget(lbl_concat)
        row_fmt.addWidget(self.txt_concat_file)
        main_layout.addLayout(row_fmt)

        # Row 5: progress + run
        row_run = QHBoxLayout()
        self.progress_bar = QProgressBar()

        self.btn_run = QPushButton("Run OCR")
        # Make "Run OCR" green
        self.btn_run.setStyleSheet("background-color: green; color: white;")

        self.btn_run.clicked.connect(self.run_ocr)
        row_run.addWidget(self.progress_bar)
        row_run.addWidget(self.btn_run)
        main_layout.addLayout(row_run)

        # Logging area
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        # Menus
        self.menu_preferences = None
        self.menu_theme = None
        self.light_action = None
        self.dark_action = None
        self.system_action = None
        self.create_menus()

        # Drag & drop
        self.setAcceptDrops(True)

        # Load settings
        self.load_settings()
        self.apply_saved_theme()

        self.ocr_thread = None

    def create_menus(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # Preferences
        self.menu_preferences = menubar.addMenu("Preferences")

        # Separate actions for default input & output
        act_default_input = QAction("Set Default Input Folder...", self)
        act_default_input.triggered.connect(self.set_default_input_folder)
        self.menu_preferences.addAction(act_default_input)

        act_default_output = QAction("Set Default Output Folder...", self)
        act_default_output.triggered.connect(self.set_default_output_folder)
        self.menu_preferences.addAction(act_default_output)

        # Theme menu
        self.menu_theme = self.menu_preferences.addMenu("Theme")

        self.light_action = QAction("Light", self, checkable=True)
        self.dark_action = QAction("Dark", self, checkable=True)
        self.system_action = QAction("System", self, checkable=True)

        self.light_action.triggered.connect(lambda: self.set_theme("Light"))
        self.dark_action.triggered.connect(lambda: self.set_theme("Dark"))
        self.system_action.triggered.connect(lambda: self.set_theme("System"))

        self.menu_theme.addAction(self.light_action)
        self.menu_theme.addAction(self.dark_action)
        self.menu_theme.addAction(self.system_action)

        # Help
        help_menu = menubar.addMenu("Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self.about_dialog)
        help_menu.addAction(about_act)

    def set_default_input_folder(self):
        msg = "Set your default input folder (where images/PDFs are stored)."
        default_in = QFileDialog.getExistingDirectory(self, msg)
        if default_in:
            self.settings.setValue("default_input_folder", default_in)
            QMessageBox.information(self, "Saved", f"Default input folder set to:\n{default_in}")

    def set_default_output_folder(self):
        msg2 = "Set your default output folder (where results go)."
        default_out = QFileDialog.getExistingDirectory(self, msg2)
        if default_out:
            self.settings.setValue("default_output_folder", default_out)
            QMessageBox.information(self, "Saved", f"Default output folder set to:\n{default_out}")

    def set_theme(self, theme: str):
        for a in [self.light_action, self.dark_action, self.system_action]:
            a.setChecked(False)

        if theme == "Light":
            self.light_action.setChecked(True)
        elif theme == "Dark":
            self.dark_action.setChecked(True)
        else:
            self.system_action.setChecked(True)

        self.settings.setValue("theme", theme)
        apply_theme(self, theme)

    def apply_saved_theme(self):
        theme_choice = self.settings.value("theme", "System")
        if theme_choice not in ["Light", "Dark", "System"]:
            theme_choice = "System"
        self.set_theme(theme_choice)

    def about_dialog(self):
        info = (
            "<h2>OCR Bulk Processor</h2>"
            "<p>This application streamlines OCR for multiple images or PDFs, "
            "with an option to produce plain text, HOCR (HTML), or multi-page searchable PDF.</p>"
            "<p>Features include:</p>"
            "<ul>"
            "<li>Easy drag-and-drop support</li>"
            "<li>Concatenation for multi-page PDF merging</li>"
            "<li>Theming options (Light, Dark, or System)</li>"
            "</ul>"
            "<p>Version 2.3 – Released April 2025<br>"
            "© 2025 by DemiGodMode<br>"
            "All rights reserved.</p>"
        )
        QMessageBox.about(self, "About OCR Bulk Processor", info)

    def load_settings(self):
        last_in = self.settings.value("last_images", "")
        last_out = self.settings.value("last_output", "")
        last_sub = self.settings.value("last_subfolders", False, type=bool)
        last_concat = self.settings.value("last_concat_state", False, type=bool)
        last_concat_file = self.settings.value("last_concat_file", "all_ocr_results.txt")
        last_format = self.settings.value("last_format", "Plain Text")

        self.txt_input.setText(last_in)
        self.txt_output.setText(last_out)
        self.chk_subfolders.setChecked(last_sub)
        self.chk_concatenate.setChecked(last_concat)
        self.txt_concat_file.setText(last_concat_file)

        idx = self.cmb_format.findText(last_format)
        if idx >= 0:
            self.cmb_format.setCurrentIndex(idx)

    def save_settings(self):
        self.settings.setValue("last_images", self.txt_input.text())
        self.settings.setValue("last_output", self.txt_output.text())
        self.settings.setValue("last_subfolders", self.chk_subfolders.isChecked())
        self.settings.setValue("last_concat_state", self.chk_concatenate.isChecked())
        self.settings.setValue("last_concat_file", self.txt_concat_file.text())
        self.settings.setValue("last_format", self.cmb_format.currentText())

    def on_format_change(self):
        # Auto-set extension in the concatenated filename
        fmt = self.cmb_format.currentText()
        fname = self.txt_concat_file.text().strip()

        if fmt.startswith("Plain"):    # "Plain Text"
            if not fname.lower().endswith(".txt"):
                self.txt_concat_file.setText("all_ocr_results.txt")
        elif "HOCR" in fmt:           # "HOCR (HTML)"
            if not fname.lower().endswith(".hocr"):
                self.txt_concat_file.setText("all_ocr_results.hocr")
        else:                         # "Searchable PDF"
            if not fname.lower().endswith(".pdf"):
                self.txt_concat_file.setText("all_ocr_results.pdf")

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images or PDF",
            "",
            "Images/PDF (*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.gif *.pdf);;All Files (*)"
        )
        if files:
            self.txt_input.setText("|".join(files))

    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.txt_output.setText(folder)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            existing = self.txt_input.text().split("|") if self.txt_input.text() else []
            for u in urls:
                existing.append(u.toLocalFile())
            self.txt_input.setText("|".join(existing))

    def run_ocr(self):
        input_str = self.txt_input.text().strip()
        output_dir = self.txt_output.text().strip()
        subfolders = self.chk_subfolders.isChecked()
        do_concat = self.chk_concatenate.isChecked()

        # Try default input if none provided
        if not input_str:
            def_in = self.settings.value("default_input_folder", "")
            if def_in and os.path.isdir(def_in):
                # gather images
                file_list = self.get_files_in_folder(def_in, subfolders)
                if not file_list:
                    QMessageBox.warning(self, "No Images Found", "No images found in default folder.")
                    return
                input_str = "|".join(file_list)
            else:
                QMessageBox.warning(self, "No Input", "Please select images or set a valid default folder.")
                return

        # Try default output if none provided
        if not output_dir:
            def_out = self.settings.value("default_output_folder", "")
            if def_out and os.path.isdir(def_out):
                output_dir = def_out
            else:
                QMessageBox.warning(self, "No Output Folder", "Please select output or set a default.")
                return

        # Build final list
        items = []
        for it in input_str.split("|"):
            it = it.strip()
            if os.path.isdir(it):
                items.extend(self.get_files_in_folder(it, subfolders))
            else:
                items.append(it)

        if not items:
            QMessageBox.warning(self, "No Files", "No valid images or PDFs found.")
            return

        # Ensure out dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Convert PDF input to images if PDF2Image installed
        final_list = []
        for f in items:
            ext = os.path.splitext(f)[1].lower()
            if ext == ".pdf":
                if not PDF_SUPPORT:
                    self.log("PDF support not installed; skipping " + os.path.basename(f))
                    continue
                # convert
                try:
                    pages = convert_from_path(f)
                    for idx, im in enumerate(pages):
                        tmp = os.path.join(output_dir, f"{os.path.basename(f)}_page_{idx}.png")
                        im.save(tmp, "PNG")
                        final_list.append(tmp)
                    self.log(f"Converted {os.path.basename(f)} -> {len(pages)} image(s).")
                except Exception as e:
                    self.log(f"Failed to convert PDF {f}: {e}")
            else:
                final_list.append(f)

        if not final_list:
            QMessageBox.warning(self, "No Valid Images", "No valid images left after PDF skipping.")
            return

        # Determine format
        fmt_choice = self.cmb_format.currentText()
        if fmt_choice.startswith("Plain"):
            out_fmt = "txt"
        elif "HOCR" in fmt_choice:
            out_fmt = "hocr"
        else:
            out_fmt = "pdf"

        concat_name = self.txt_concat_file.text().strip()

        # Save current settings
        self.save_settings()

        # Clear log
        self.log_area.clear()
        self.progress_bar.setValue(0)

        # Spawn background thread
        self.ocr_thread = OCRWorker(
            file_list=final_list,
            output_dir=output_dir,
            concatenate=do_concat,
            output_format=out_fmt,
            concat_filename=concat_name
        )
        self.ocr_thread.progress_signal.connect(self.log)
        self.ocr_thread.done_signal.connect(self.ocr_done)
        self.ocr_thread.progress_bar_signal.connect(self.progress_bar.setValue)

        self.btn_run.setEnabled(False)
        self.ocr_thread.start()

    def ocr_done(self):
        self.log("All OCR tasks completed.")
        self.btn_run.setEnabled(True)

    def get_files_in_folder(self, folder: str, recurse: bool):
        exts = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.tif", "*.tiff", "*.pdf"]
        paths = []
        p = Path(folder)
        if recurse:
            for e in exts:
                paths.extend(p.rglob(e))
        else:
            for e in exts:
                paths.extend(p.glob(e))
        return [str(x) for x in sorted(paths)]

    def log(self, msg: str):
        self.log_area.appendPlainText(msg)