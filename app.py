"""## main GUI for the finance manager program
"""
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QHBoxLayout, QMainWindow, QVBoxLayout, QWidget,
                             QTextEdit, QLineEdit, QApplication, QPushButton,
                             QLabel, QScrollArea)
from finance_manager import Manager


class ManagerWindow(Manager, QMainWindow):
    """## _summary_
        Creates a desktop app to interogate financial data.

    ### Args:
        - `Manager (obj)`: inherits from
        - `QMainWindow (obj)`: inherits from
    """

    def __init__(self, path):
        Manager.__init__(self, path)
        QMainWindow.__init__(self)
        self.setWindowTitle("Scrollable Layout Example")
        self.setGeometry(100, 100, 600, 300)

        # Scroll Area Setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        # Main Container Widget
        self.main_container = QWidget()
        self.scroll_area.setWidget(self.main_container)
        self.main_layout = QVBoxLayout(self.main_container)

        # Place Holder Label
        self.main_layout.addWidget(
            QLabel("Place data tile plots here. Budget plot, spending and one other"))

        # Horizontal Scroll Space 1 Setup
        self.setup_h_scroll_space1()

        # Middle Layout for Account Information
        self.setup_middle_layout()

        # Horizontal Scroll Space 2 Setup
        self.main_layout.addWidget(QLabel("Upcoming Bills"))
        self.setup_h_scroll_space2()

        # Bottom Layout
        self.setup_btm_layout()

    def setup_h_scroll_space1(self):
        """Creates a horizontal scroll area in window for plots.
        Uses QHBoxLayout.
        """
        h_scroll_area1 = QScrollArea()
        h_scroll_area1.setWidgetResizable(True)
        h_scroll_area1.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        h_scroll_area1.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_widget1 = QWidget()  # This will contain the QHBoxLayout
        h_scroll_area1.setWidget(scroll_widget1)

        # Set the layout for the container widget
        top_layout = QHBoxLayout(scroll_widget1)

        # budget_plot = self.plot_budget(month='test')
        expense_cat_plot = self.plot_expense_categories(month='test')
        # top_layout.addWidget(budget_plot)
        top_layout.addWidget(expense_cat_plot)

        # Optionally, adjust the container widget's size based on the number of plots
        # Adjust based on the number of plots and their spacing
        total_width = 500 * 20  # Adjust based on the actual number of plots and their spacing
        scroll_widget1.setMinimumWidth(total_width)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(h_scroll_area1)

    def setup_middle_layout(self):
        """Creates a middle area in window.
           Uses QVBoxLayout.
        """
        middle1_layout = QVBoxLayout()
        middle1_label = QLabel("Add accounts")
        middle1_layout.addWidget(middle1_label)
        self.main_layout.addLayout(middle1_layout)

    def setup_h_scroll_space2(self):
        """Creates a horizontal scroll aread.
           Uses QHboxLayout.
        """
        h_scroll_area2 = QScrollArea()
        h_scroll_area2.setWidgetResizable(True)
        h_scroll_area2.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        h_scroll_area2.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_widget2 = QWidget()
        h_scroll_area2.setWidget(scroll_widget2)
        middle2_layout = QHBoxLayout(scroll_widget2)
        for i in range(20):
            button = QPushButton(f"Button {i+1}")
            middle2_layout.addWidget(button)
        self.main_layout.addWidget(h_scroll_area2)

    def setup_btm_layout(self):
        """Creates a bottom area in the window.
           Uses QVBoxLayout.
        """
        bottom_layout = QVBoxLayout()
        bottom_label = QLabel("Recent Transactions")
        bottom_layout.addWidget(bottom_label)
        self.main_layout.addLayout(bottom_layout)


if __name__ == "__main__":
    DATA_PATH = r"C:\Users\Owner\Desktop\finances\2024\test"
    # Create the application instance
    app = QApplication(sys.argv)

    # Create a main window instance
    window = ManagerWindow(path=DATA_PATH)
    window.show()
    try:
        app.exec()
    except SystemExit:
        pass
