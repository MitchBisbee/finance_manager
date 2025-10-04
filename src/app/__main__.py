"""Main entry point for the module.
"""
# pylint: disable=no-name-in-module
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow
from managers.finances import FinanceManager
from processing.cleaners import CSVDataCleaner


def main() -> None:
    """Entry point to the app.
    """
    data_path = ""
    cleaner = CSVDataCleaner(path=Path(data_path))
    df_list = cleaner.load_and_clean()
    app = QApplication(sys.argv)
    window = MainWindow(
        finance_manager=FinanceManager(data_frame_list=df_list)
    )
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
