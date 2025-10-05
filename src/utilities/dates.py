
from __future__ import annotations
import pandas as pd

def current_month_range() -> tuple[pd.Timestamp, pd.Timestamp]:
    """(first of this month, today)"""
    today = pd.Timestamp.today().normalize()
    start = today.replace(day=1)
    return start, today

def previous_month_range() -> tuple[pd.Timestamp, pd.Timestamp]:
    """(first of prev month, last of prev month)"""
    today = pd.Timestamp.today().normalize()
    start = today.replace(day=1) - pd.DateOffset(months=1)
    end = today.replace(day=1) - pd.DateOffset(days=1)
    return start, end

def last_three_months_to_today() -> tuple[pd.Timestamp, pd.Timestamp]:
    """(first of month two months ago, today) — rolling 3-month window incl. current"""
    today = pd.Timestamp.today().normalize()
    start = today.replace(day=1) - pd.DateOffset(months=2)
    return start, today

def prev_three_full_months() -> tuple[pd.Timestamp, pd.Timestamp]:
    """three full months before current month (e.g., if Oct → Jul 1 .. Sep 30)"""
    today = pd.Timestamp.today().normalize()
    end = today.replace(day=1) - pd.DateOffset(days=1)
    start = today.replace(day=1) - pd.DateOffset(months=3)
    return start, end
