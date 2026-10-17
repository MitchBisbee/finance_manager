"""Module for analyzing finances and creating budgets."""
# pylint: disable=no-name-in-module
from typing import List
import pandas as pd
from plotly.io import to_html
from utilities.plot_generator import PlotlyPlots
from config import filters_config
from utilities.dates import (current_month_range, previous_month_range,
                             last_three_months_to_today)


class FinanceService:
    """Class for interrogating financial data, and creating budgets."""

    def __init__(self, data_frame_list: List[dict]) -> None:
        self._data_frames = data_frame_list
        self._checking_df = self._set_checking_df()
        self._credit_df = self._set_credit_df()
        self._concat_df = self._set_concat_df()

    def _set_checking_df(self):
        """Setter
        """
        return next(
            (item.get("checking")
             for item in self._data_frames if item.get("checking") is not None),
            None
        )

    def _set_credit_df(self):
        """Setter
        """
        return next(
            (item.get("credit")
             for item in self._data_frames if item.get("credit") is not None),
            None
        )

    def _set_concat_df(self):
        """Setter
        """
        return pd.concat([self._checking_df, self._credit_df], ignore_index=True)

    def expense_categories(self, month_interval: str = None) -> pd.DataFrame:
        """Groups a data frame into expense categories.
        Args:
            month_interval (str): "current_month", "previous_month","three_month"
        Returns:
            pandas.core.groupby.DataFrameGroupBy: GroupBy object with data grouped
            into expense categories.
        """
        copy_df = self._concat_df.copy()
        interval_dict = {"current_month": current_month_range(),
                         "previous_month": previous_month_range(),
                         "three_months": last_three_months_to_today()}

        start, end = interval_dict.get(month_interval, (None, None))
        if start is None or end is None:
            return abs(copy_df.groupby("category")["amount"].sum())

        copy_df["date"] = pd.to_datetime(copy_df["date"], errors="coerce")
        mask = (copy_df["date"] >= start) & (copy_df["date"] <= end)
        copy_df = copy_df.loc[mask]
        return abs(copy_df.groupby("category")["amount"].sum())

    def plot_expenses_versus_income(self, month_interval=None):
        """Plots a bar chart showing expensis versus income for a month.
        """
        expensis = self.total_expensis_last_month()
        income = self.total_income_last_month()
        data = {"x": ["expenses", "income"], "y": [
            expensis, income],  "name": "expenses vs income",
            "title": "Expensis vs Income"}
        fig = PlotlyPlots().bar_chart(data)
        return to_html(fig, full_html=False, include_plotlyjs='cdn')

    def plot_expense_categories(self, month_interval=None):
        """Plots the expense categories in a pie chart.
           Args:
             month_interval (str): "current_month", "previous_month",
             "three_month"
        """
        grouped_data = self.expense_categories(month_interval=month_interval)
        if grouped_data is not None:
            data = {'labels': grouped_data.index,
                    'values': grouped_data.values,
                    'name': "Categorical Expenses",
                    'title': "Categorical Expenses"}
            fig = PlotlyPlots.pie_chart(data)
            return to_html(fig, full_html=False, include_plotlyjs='cdn')
        else:
            print("Data could not be plotted.")

    def get_current_month_credit_usage(self):
        """Gets the amount spent on the credit card for the month.

        Returns:
            float64: Amount spent in monthly period.
        """
        start, end = current_month_range()
        copy_df = self._credit_df.copy()
        copy_df["date"] = pd.to_datetime(copy_df["date"], errors="coerce")
        mask = (copy_df["date"] >= start) & (copy_df["date"] <= end)
        copy_df = copy_df.loc[mask]
        return abs(copy_df.loc[copy_df["amount"] < 0, "amount"].sum())

    def get_previous_month_credit_usage(self):
        """Gets the amount spent on the credit card for the previous month.

        Returns:
            float64: Amount spent in monthly period.
        """
        start, end = previous_month_range()
        copy_df = self._credit_df.copy()
        copy_df["date"] = pd.to_datetime(copy_df["date"], errors="coerce")
        mask = (copy_df["date"] >= start) & (copy_df["date"] <= end)
        copy_df = copy_df.loc[mask]
        return abs(copy_df.loc[copy_df["amount"] < 0, "amount"].sum())

    def total_income_last_month(self):
        """Calculates the total monthly income of the prevous month.

        Returns:

            float: Sum of positive numbers in Amount for previous month.
        """
        start, end = previous_month_range()
        mask = (self._checking_df["date"] >= start) & (
            self._checking_df["date"] <= end)
        last_month = self._checking_df.loc[mask]
        income = last_month.loc[last_month["amount"] > 0, "amount"].sum()
        return income

    def total_expensis_last_month(self):
        """Computes the total amount spent in the previos month.

        Returns:
            float: total amount spent in a period
        """
        start, end = previous_month_range()
        df = self._checking_df
        mask = (df["date"] >= start) & (df["date"] <= end)
        last_month = df.loc[mask]
        return abs(last_month.loc[last_month["amount"] < 0, "amount"].sum())

    def set_budget(self, df):
        """Creates a budget based on categories in a personal finance dataframe.

        Args:
            df (pd.DataFrame): data frame of personal finanances
        """
        return df

    def get_subscriptions(self) -> pd.DataFrame:
        """Identifies and returns a data frame of subscriptions.
        Returns:
            pd.DataFrame | None: Summary of recurring payments.
        """
        start, end = last_three_months_to_today()
        copy_df = self._concat_df.copy()
        copy_df["date"] = pd.to_datetime(copy_df["date"], errors="coerce")
        mask = (copy_df["date"] >= start) & (
            copy_df["date"] <= end)
        copy_df = copy_df.loc[mask]
        filtered = copy_df[~copy_df["category"].isin(
            filters_config["exclude_list"])]
        subscription_names = (
            filtered["description"]
            .value_counts()
            .loc[lambda x: x > 1]
            .index
        )
        duplicate_subscr_data = filtered[filtered["description"].isin(
            subscription_names)]
        duplicate_subscr_data.loc[:,
                                  "amount"] = duplicate_subscr_data["amount"].abs()
        return (duplicate_subscr_data.
                drop_duplicates(subset=["description"], keep="first"))

    if __name__ == "__main__":
        pass
