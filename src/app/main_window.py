"""Main GUI for the finance manager program (PySide6 version)."""


# pylint: disable=no-name-in-module
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from managers.finances import FinanceManager
# TODO: there is too much space between th pi chart and the legend.
# TODO: The UI needs a redesign, there should be three main plots, expensis,
# spending vs income and budget, that's it
# then we will have the subscriptions underneath the three plots in card format
# one card = one subscription with subscription name and cost
# use a parent container as a Vbox and the plot area will be an HBox with
# a normal styled empty widget per plot
# second layer will be and Hbox with the a card for each subscription
# then at on the third layer will be buttons, styled and evenly spaced


class MainWindow(QMainWindow):
    """
    Creates a desktop app to interrogate financial data.

    Args:
        QMainWindow (obj): Qt main window
    """

    def __init__(self, finance_manager: FinanceManager):
        QMainWindow.__init__(self)
        self._finance_manager = finance_manager
        self.setWindowTitle("Finance Manager")
        self.setGeometry(100, 100, 900, 600)

        # Scroll Area Setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        # Main Container Widget
        self.main_container = QWidget()
        self.scroll_area.setWidget(self.main_container)
        self.main_layout = QVBoxLayout(self.main_container)

        # Placeholder Label
        self.main_layout.addWidget(
            QLabel("Place data tile plots here. Budget plot, spending and one other")
        )

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
        """Creates a horizontal scroll area in window for plots. Uses QHBoxLayout."""
        h_scroll_area1 = QScrollArea()
        h_scroll_area1.setWidgetResizable(True)
        h_scroll_area1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        h_scroll_area1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget1 = QWidget()  # This will contain the QHBoxLayout
        h_scroll_area1.setWidget(scroll_widget1)

        # Set the layout for the container widget
        top_layout = QHBoxLayout(scroll_widget1)

        # Example plot widgets from Manager API
        # budget_plot = self.plot_budget(month="test")
        expense_cat_plot = self._finance_manager.plot_expense_categories()
        # top_layout.addWidget(budget_plot)
        if expense_cat_plot is not None:
            top_layout.addWidget(expense_cat_plot)
        else:
            top_layout.addWidget(QLabel("No expense chart available"))
        # Optionally, adjust the container widget's size based on the number of plots
        total_width = 500 * 20  # tune based on actual plot widget widths
        scroll_widget1.setMinimumWidth(total_width)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(h_scroll_area1)

    def setup_middle_layout(self):
        """Creates a middle area in window. Uses QVBoxLayout."""
        middle1_layout = QVBoxLayout()
        middle1_label = QLabel("Add accounts")
        middle1_layout.addWidget(middle1_label)
        self.main_layout.addLayout(middle1_layout)

    def setup_h_scroll_space2(self):
        """Creates a horizontal scroll area. Uses QHBoxLayout."""
        h_scroll_area2 = QScrollArea()
        h_scroll_area2.setWidgetResizable(True)
        h_scroll_area2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        h_scroll_area2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget2 = QWidget()
        h_scroll_area2.setWidget(scroll_widget2)

        middle2_layout = QHBoxLayout(scroll_widget2)
        for i in range(20):
            button = QPushButton(f"Button {i + 1}")
            middle2_layout.addWidget(button)

        self.main_layout.addWidget(h_scroll_area2)

    def setup_btm_layout(self):
        """Creates a bottom area in the window. Uses QVBoxLayout."""
        bottom_layout = QVBoxLayout()
        bottom_label = QLabel("Recent Transactions")
        bottom_layout.addWidget(bottom_label)
        self.main_layout.addLayout(bottom_layout)


if __name__ == "__main__":
    pass
