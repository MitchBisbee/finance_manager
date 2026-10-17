"""Main entry point for the module.
"""
# pylint: disable=no-name-in-module
import sys

from pathlib import Path
from PySide6.QtWidgets import QApplication
from finance_manager.app.main_window import MainWindow
from finance_manager.services.finances import FinanceService
from finance_manager.utilities.cleaners import CSVDataCleaner
from finance_manager.config import load_stylesheet


def main() -> None:
    """Entry point to the app.
    """
    data_path = r"C:\Users\Owner\Desktop\finances\2025\JUL-SEP"
    cleaner = CSVDataCleaner(path=Path(data_path))
    df_list = cleaner.load_and_clean()
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = MainWindow(
        finance_manager=FinanceService(data_frame_list=df_list)
    )
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
