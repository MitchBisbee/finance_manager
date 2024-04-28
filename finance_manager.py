"""Module for analyzing finances and creating budgets.

Functions:
    fill_self._data_frames(path: str) -> dict:
        Reads self._data_frames from the given path and returns a dictionary of data.

    expense_categories(df: pd.DataFrame) -> pd.DataFrame:
        Groups the given DataFrame into expense categories.
    
    create_df(file: Path | str) -> dict | pd.DataFrame
        Creates a data frame or dictionary data from file input

    credit_expenses(df: pd.DataFrame) -> pandas.core.groupby.DataFrameGroupBy:
        Groups credit expenses from the DataFrame by categories.

    total_monthly_pay() -> float:
        Calculates the total monthly pay from the financial data.

    amount_spent(df: pd.DataFrame) -> float:
        Computes the total amount spent within a given period.

    calculate_net_expenses(df: pd.DataFrame) -> float:
        Calculates net expenses after income for a given period.

    notify_budget_status(budget: float, df: pd.DataFrame) -> str:
        Notifies if you are on, over, or under budget based on the given DataFrame.

    set_budget(df: pd.DataFrame) -> pd.DataFrame:
        Sets a budget based on the analysis of the given DataFrame.

    show_subscriptions(df: pd.DataFrame) -> pd.DataFrame:
        Identifies and displays subscription payments from the DataFrame.
"""
from pathlib import Path
import pandas as pd
from plotly.io import to_html
from PyQt6.QtWebEngineWidgets import QWebEngineView
from plot_generator import PlotlyPlots

# the budget_plot function needs fine tuning, it is showing up in the GUI
# it is not the right data, I think using groupby would work better
# need to add a drop down box so that I can chose what months data I want
# to look at
# need to add the other plot functions as well
# a spending bar charts
# and a line graph


class Manager:
    """## Class for interogating financial data
    """

    def __init__(self, path) -> None:
        self.path = path
        self._data_frames = {}
        self.load_data_frames(path)
        self.months = list(self._data_frames.keys())
        self.VACP_PAY = 2241.91
        self.JOB_PAY1 = 2307.93
        self.JOB_PAY2 = 2307.93

    @property
    def data_frames(self):
        """Getter

        Returns:
            dict: dict of pd.DataFrame
        """
        return self._data_frames

    def load_data_frames(self, path):
        """Loads DataFrames from CSV files in the given directory path."""
        directory_path = Path(path)

        if not directory_path.is_dir():
            print(f"Error: {path} is not a directory.")
            return

        temp_data_frames = {}
        for file_name in directory_path.glob("**/*.csv"):  # Assuming CSV files
            if file_name.is_file():
                key = file_name.parent.stem

                try:
                    df = pd.read_csv(file_name)
                    if key not in temp_data_frames:
                        temp_data_frames[key] = []
                    temp_data_frames[key].append(df)
                except Exception as e:
                    print(f"Failed to read {file_name}: {e}")

        self._data_frames = temp_data_frames

    def expense_categories(self, month):
        """Groups a data frame into expense categories.

        Args:
            month(str): month of personal finances

        Returns:
            pandas.core.groupby.DataFrameGroupBy: GroupBy object with data grouped
            into expense categories.
        """
        if month not in self.months:
            print("Error: Month not found.")
            return None
        return self._data_frames[month][0].groupby("Category")['Amount'].sum()

    def plot_budget(self, month):
        """Generates a pie chart to show budget use.

        Returns:
                list: the plot window and x and y dimensions
        """
        if month not in self.months:
            print("Error: Month not found.")
            return None
        else:
            df = self._data_frames[month][0]
            values = df[df.columns[8]].fillna(0).clip(lower=0)
            labels = df[df.columns[10]]
            data = {'Labels':  labels,
                    'Values': values}
            plot = PlotlyPlots(data)
            fig = plot.pie_chart()
            # Convert the Plotly figure to HTML
            html_string = to_html(fig, full_html=False, include_plotlyjs='cdn')

            # Create a QWebEngineView to display the HTML
            webview = QWebEngineView()
            webview.setHtml(html_string)
            return webview

    def plot_expense_categories(self, month):
        """Plots the expense categories in a pie chart using Plotly."""
        if month not in self.months:
            print("Error: Month not found.")
            return None

        grouped_data = self.expense_categories(month)
        if grouped_data is not None:
            # Assuming 'grouped_data' is a Series with categories as index and summed amounts as values
            data = {'Labels': grouped_data.index,
                    'Values': grouped_data.values}
            plot = PlotlyPlots(data)
            fig = plot.pie_chart()

            # Convert the Plotly figure to HTML
            html_string = to_html(fig, full_html=False, include_plotlyjs='cdn')

            # Create a QWebEngineView to display the HTML
            webview = QWebEngineView()
            webview.setHtml(html_string)
            return webview
        else:
            print("Data could not be grouped.")

    def create_df(self, file):
        """Creates a pandas data frame from a .csv or .xlsx file

        Args:
            file (str,Path): .csv or .xlsx file

        Returns:
            pd.DataFrame: data frame from the file input if .csv extenstion

            or

            dict: dictionary of data frames with sheets as keys if .xlsx extension
        """
        if isinstance(file, str):
            if file.endswith(".csv"):
                return pd.read_csv(file)
            if file.endswith(".xlsx"):
                return pd.read_excel(file, sheet_name=None)
        elif isinstance(file, Path):
            if file.suffix == ".csv":
                return pd.read_csv(file)
            if file.suffix == ".xlsx":
                return pd.read_excel(file, sheet_name=None)
        else:
            return None

    def credit_expensis(self, df):
        """Groups the incoming data frame into credit expense categories.

        Args:
            df (pd.DataFrame): data frame of personal finances

        Returns:
            pandas.core.groupby.DataFrameGroupBy: GroupBy object with credit usage
            grouped into expense categories.
        """

        if not isinstance(df, pd.DataFrame):
            print("Error, only Dataframe objects are permitted.")
            return None
        return df.groupby(["Account Type", "Institution Name"])["Amount"].sum()

    def total_monthly_pay(self):
        """Calculates total monthly pay.

        Returns:
            float: total monthly pay
        """
        return self.VACP_PAY + self.JOB_PAY1 + self.JOB_PAY2

    def amount_spent(self, df):
        """Computes the total amount spent from the incoming personal finance data frame.

        Args:
            df (pd.DataFrame): data frame of personal finanances

        Returns:
            float: total amount spent in a period
        """
        if not isinstance(df, pd.DataFrame):
            print("Error, only Dataframe objects are permitted.")
            return None
        return df["Amount"].sum()

    def calculate_net_expensis(self, df):
        """Computes the amount spent in pay period.

        Args:
        df (pd.DataFrame): data frame of personal finanances
        Returns:
            float: net amount spent
        """
        if not isinstance(df, pd.DataFrame):
            print("Error, only Dataframe objects are permitted.")
            return None
        return df["Amount"].sum() - self.total_monthly_pay()

    def notify_budget_status(self, budget, df):
        """Notifies if you are on, over, or under budget based on financial data analysis.

        Args:
        budget (float): The budget amount for a specific period (e.g., monthly, yearly, quarterly).
        This should correspond to the period of the financial data being analyzed.

            df (pd.DataFrame): data frame of personal finanances

        Returns:
            str: A message indicating whether you are on, over, or under budget and by how much.

        Example:
        >>> notify_budget_status(1200.00)
        'You are under budget by $100.00 this month.'
        """
        if self.amount_spent(df) == budget:
            return "You are On budget"
        elif self.amount_spent(df) > budget:
            return f"You are over budget by {self.amount_spent(df) - budget}."
        else:
            return f"You are under budget by {budget - self.amount_spent(df)}"

    def set_budget(self, df):
        """Creates a budget based on catagories in a personal finance dataframe.

        Args:
        df (pd.DataFrame): data frame of personal finanances
        """
        return df

    def __single_mode(self, series):
        """ Custom aggregation function for mode that ensures a single value

        Args:
            series (pd.Series): series to calculate the mode

        Returns:
            pd.Series: series of modes
        """
        modes = pd.Series.mode(series)
        if len(modes) > 1:  # If there's more than one mode, pick the first one
            return modes.iloc[0]
        else:
            return modes

    def show_subscriptions(self, df):
        """Identifies recurring payments classified under a specific category
        in a personal finance DataFrame and returns a summary with the payment
        name, amount, and typical day of the month for the payment.

        Args:
            df (pd.DataFrame): DataFrame of personal finances.

        Returns:
            pd.DataFrame: Summary of recurring payments.
        """
        if not isinstance(df, pd.DataFrame):
            print("Error, only DataFrame objects are permitted.")
            return None
        df['Date'] = pd.to_datetime(df.iloc[:, 0])
        df['day_of_month'] = df['Date'].dt.day
        category_filter = df.iloc[:, 10] == "Entertainment & Rec."
        filtered_df = df[category_filter]
        # Where the magic happens
        recurring = filtered_df.groupby([df.columns[6], df.columns[8]])[
            'day_of_month'].agg([('Day of Month', self.__single_mode), ('Count', 'count')])
        # Filter for actual recurring payments
        recurring = recurring[recurring['Count'] > 1]
        recurring.reset_index(inplace=True)
        # Drop the count column if it's no longer needed
        recurring.drop(columns=['Count'], inplace=True)
        # Rename columns for clarity
        recurring.columns = ['Name', 'Amount', 'Day of Month']
        return recurring


if __name__ == "__main__":
    pass
