"""Main entry point for the module.
"""
# pylint: disable=no-name-in-module
import os
import sys

from pathlib import Path
from PySide6.QtWidgets import QApplication, QFileDialog
from finance_manager.app.main_window import MainWindow
from finance_manager.services.finances import FinanceService
from finance_manager.utilities.cleaners import CSVDataCleaner
from finance_manager.config import load_stylesheet


def _get_data_path() -> str:
    """Returns the CSV data directory or file.

    Uses the first command line argument, then the FINANCE_DATA_DIR
    environment variable, then prompts for a directory.
    """
    if len(sys.argv) > 1:
        return sys.argv[1]
    if os.environ.get("FINANCE_DATA_DIR"):
        return os.environ["FINANCE_DATA_DIR"]
    return QFileDialog.getExistingDirectory(
        None, "Select a folder of transaction CSV files")


def main() -> None:
    """Entry point to the app.
    """
    app = QApplication(sys.argv)
    load_stylesheet(app)
    data_path = _get_data_path()
    df_list = (CSVDataCleaner(path=Path(data_path)).load_and_clean()
               if data_path else [])
    window = MainWindow(
        finance_manager=FinanceService(data_frame_list=df_list)
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
