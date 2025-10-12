"""Main GUI for the finance manager program (PySide6 version)."""

# pylint: disable=no-name-in-module
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QComboBox,
    QFileDialog,
    QSizePolicy
)
from utilities.constants import SUBSCRIPTIONS_TABLE_HEADERS, SNAPSHOT_MAP
from managers.finances import FinanceManager


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
        self.month_view_combo = None
        self.month_interval = "previous_month"
        # Scroll Area Setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        # Main Container Widget
        self.main_container = QWidget()
        self.scroll_area.setWidget(self.main_container)
        self.main_layout = QVBoxLayout(self.main_container)
        self.setup_controls_area()
        self.setup_plot_area()

        # Middle Layout to show spending by category and subscriptions
        self.setup_middle_layout()

    def setup_plot_area(self) -> None:
        """Creates a plot area displaying the expense category chart."""
        expenses_html = self._finance_manager.plot_expense_categories(
            month_interval=self.month_interval)
        expenses_vs_income_html = self._finance_manager.plot_expenses_versus_income()
        expenses_widget = QWebEngineView()
        expenses_widget.setHtml(expenses_html)

        expenses_vs_income_widget = QWebEngineView()
        expenses_vs_income_widget.setHtml(expenses_vs_income_html)

        plot_layout = QHBoxLayout()
        plot_layout.addWidget(expenses_widget)
        plot_layout.addWidget(expenses_vs_income_widget)

        plot_container = QWidget()
        plot_container.setLayout(plot_layout)

        self.main_layout.addWidget(plot_container)

    def setup_controls_area(self) -> None:
        """Creates a button area in the window using QHBoxLayout."""
        parent_layout = QHBoxLayout()
        parent_layout.setContentsMargins(16, 12, 16, 12)
        parent_layout.setSpacing(12)

        # ----- Load Data Section -----
        loader_label = QLabel("Load data:")
        loader_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        load_button = QPushButton("Browse…")
        load_button.setObjectName("secondary")  # styled via stylesheet
        load_button.clicked.connect(self._open_file_dialog)

        # ----- Month Snapshot Section -----
        month_view_label = QLabel("Spending snapshot:")
        month_view_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.month_view_combo = QComboBox()
        self.month_view_combo.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.month_view_combo.addItems(list(SNAPSHOT_MAP.keys()))
        self.month_view_combo.currentIndexChanged.connect(
            self._on_snapshot_changed)

        # ----- Assemble Layout -----
        parent_layout.addWidget(loader_label)
        parent_layout.addWidget(load_button)
        parent_layout.addSpacing(20)
        parent_layout.addWidget(month_view_label)
        parent_layout.addWidget(self.month_view_combo)
        parent_layout.addStretch()  # keeps controls left-aligned

        self.main_layout.addLayout(parent_layout)

    def setup_middle_layout(self):
        """Creates a middle area with two side-by-side tables:
        Categories and Subscriptions (from a DataFrame)."""
        parent_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left: Categories
        categories_table = self._build_categories_table()
        splitter.addWidget(categories_table)

        # Right: Subscriptions (DataFrame: date, description, category, amount)
        subs_df = self._finance_manager.get_subscriptions()

        subscriptions_table = self._build_subscriptions_table_from_df(subs_df)
        splitter.addWidget(subscriptions_table)

        # Initial ratio
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 2)

        parent_layout.addWidget(splitter)
        self.main_layout.addLayout(parent_layout)

    # -----------------------
    # Private helpers
    # -----------------------
    def _build_table(self, headers, rows, right_align_cols=None, stretch_col=0):
        """Build a non-editable QTableWidget with header styling and same sizing."""
        right_align_cols = set(right_align_cols or [])
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                text = "" if val is None else str(val)
                item = QTableWidgetItem(text)
                if c in right_align_cols:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                table.setItem(r, c, item)

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        # one stretch column for pleasant fill; others size to contents
        for idx in range(len(headers)):
            if idx == stretch_col:
                header.setSectionResizeMode(idx, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)

        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        # Optional: enable sorting by clicking headers
        table.setSortingEnabled(True)
        return table

    def _build_categories_table(self):
        """Create table from expense_categories() -> dict {category: amount}."""
        data = self._finance_manager.expense_categories(
            month_interval="previous_month")
        rows = []
        for cat, amt in data.items():
            amt_text = f"${amt:,.2f}" if isinstance(
                amt, (int, float)) else ("" if amt is None else str(amt))
            rows.append((cat, amt_text))
        table = self._build_table(
            ["Category", "Amount"], rows, right_align_cols={1}, stretch_col=0)
        return table

    def _build_subscriptions_table_from_df(self, df):
        """Expect a DataFrame with columns: date, description, category, amount."""
        headers = SUBSCRIPTIONS_TABLE_HEADERS
        rows = []

        if df is not None and not df.empty:
            cols = SUBSCRIPTIONS_TABLE_HEADERS
            df = df.reindex(columns=cols)

            try:
                df["date"] = df["date"].dt.strftime("%Y-%m-%d")
            except Exception:
                df["date"] = df["date"].astype(str)

            def _fmt_amount(x):
                return f"${x:,.2f}" if isinstance(x, (int, float)) else ("" if x is None else str(x))
            df["amount"] = df["amount"].apply(_fmt_amount)

            rows = list(df.itertuples(index=False, name=None))

        return self._build_table(headers, rows, right_align_cols={3}, stretch_col=1)

    def _open_file_dialog(self):
        """Opens a file dialog to select and load financial data."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")

        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                if hasattr(self._finance_manager, "load_data"):
                    try:
                        self._finance_manager.load_data(file_path)
                        # Optional: feedback / logging hook
                        if hasattr(self, "_update_status"):
                            self._update_status(f"Loaded: {file_path}")
                    except Exception as e:
                        print(f"Error loading file: {e}")

    def _on_snapshot_changed(self):
        """Handles combo box selection change for spending snapshot."""
        selected_text = self.month_view_combo.currentText()
        self.month_interval = SNAPSHOT_MAP.get(selected_text)


if __name__ == "__main__":
    pass
