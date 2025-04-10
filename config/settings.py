from PySide6.QtCore import QSettings


def create_qsettings():
    """
    Returns a QSettings instance for the application.
    """
    return QSettings("MyCompany", "OcrBulkProcessorV4")
