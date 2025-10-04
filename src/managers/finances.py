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
# pylint: disable=no-name-in-module
from typing import List
import pandas as pd
from plotly.io import to_html
from PySide6.QtWebEngineWidgets import QWebEngineView
from plotting.plot_generator import PlotlyPlots


class FinanceManager:
    """Class for interrogating financial data."""

    def __init__(self, data_frame_list: List[dict]) -> None:
        self._data_frames = data_frame_list
        self.months = list(self._data_frames.keys())

    @property
    def data_frames(self):
        """Getter

        Returns:
            List[dict]: dict of pd.DataFrame
        """
        return self._data_frames

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
        return self._data_frames[month][0].groupby("category")['amount'].sum()

    def plot_budget(self, month):
        """Generates a pie chart to show budget use.

        Returns:
            QWebEngineView | None: the web view widget containing the plot
        """
        if month not in self.months:
            print("Error: Month not found.")
            return None
        else:
            df = self._data_frames[month][0]
            values = df[df.columns[8]].fillna(0).clip(lower=0)
            labels = df[df.columns[10]]
            data = {'Labels': labels, 'Values': values}
            plot = PlotlyPlots(data)
            fig = plot.pie_chart()

            # Convert the Plotly figure to HTML
            html_string = to_html(fig, full_html=False, include_plotlyjs='cdn')

            # Create a QWebEngineView to display the HTML (PySide6)
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
            data = {'Labels': grouped_data.index,
                    'Values': grouped_data.values}
            plot = PlotlyPlots(data)
            fig = plot.pie_chart()

            # Convert the Plotly figure to HTML
            html_string = to_html(fig, full_html=False, include_plotlyjs='cdn')

            # Create a QWebEngineView to display the HTML (PySide6)
            webview = QWebEngineView()
            webview.setHtml(html_string)
            return webview
        else:
            print("Data could not be grouped.")

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

    def total_income_last_month(self):
        """Calculates the total monthly income of the prevous month.

        Returns:

            float: Sum of positive numbers in Amount for previous month.
        """
        start, end = self._get_previous_month_range()
        for d in self._data_frames:
            df = d.get("checking", None)
            if df is None:
                continue
        last_month = df.loc[(df["date"] >= start) & df["date"] <= end]
        income = last_month.loc[last_month["amount"] > 0, "amount"].sum()

        return income

    def total_expensis_last_month(self):
        """Computes the total amount spent in the previos month.

        Args:
            df (pd.DataFrame): data frame of personal finanances

        Returns:
            float: total amount spent in a period
        """
        start, end = self._get_previous_month_range()
        for d in self._data_frames:
            df = d.get("checking", None)
            if df is None:
                continue
        last_month = df.loc[(df["date"] >= start) & df["date"] <= end]
        income = last_month.loc[last_month["amount"] < 0, "amount"].sum()

        return abs(income)

    def set_budget(self, df):
        """Creates a budget based on categories in a personal finance dataframe.

        Args:
            df (pd.DataFrame): data frame of personal finanances
        """
        return df

    def _single_mode(self, series):
        """Custom aggregation function for mode that ensures a single value

        Args:
            series (pd.Series): series to calculate the mode

        Returns:
            pd.Series | scalar: single mode value
        """
        modes = pd.Series.mode(series)
        if len(modes) > 1:
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
            pd.DataFrame | None: Summary of recurring payments.
        """
        if not isinstance(df, pd.DataFrame):
            print("Error, only DataFrame objects are permitted.")
            return None
        df['date'] = pd.to_datetime(df.iloc[:, 0])
        df['day_of_month'] = df['Date'].dt.day
        category_filter = df.iloc[:, 10] == "Entertainment & Rec."
        filtered_df = df[category_filter]

        recurring = filtered_df.groupby([df.columns[6], df.columns[8]])['day_of_month'].agg(
            [('Day of Month', self._single_mode), ('Count', 'count')]
        )

        recurring = recurring[recurring['Count'] > 1]
        recurring.reset_index(inplace=True)
        recurring.drop(columns=['Count'], inplace=True)
        recurring.columns = ['Name', 'Amount', 'Day of Month']
        return recurring

    def _get_previous_month_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        """
        Returns the start and end dates of the previous month as pandas Timestamps.

        Example:
            get_previous_month_range()
            (Timestamp('2025-09-01 00:00:00'), Timestamp('2025-09-30 00:00:00'))
        """
        today = pd.Timestamp.today().normalize()

        start_prev_month = today.replace(day=1) - pd.DateOffset(months=1)

        end_prev_month = today.replace(day=1) - pd.DateOffset(days=1)

        return start_prev_month, end_prev_month

    if __name__ == "__main__":
        pass
