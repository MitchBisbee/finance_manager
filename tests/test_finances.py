"""A testing module to test the finances module.
"""
from pathlib import Path
from typing import List, Dict
from uuid import uuid4
import numpy as np
import pandas as pd
import pytest

from managers.finances import FinanceManager


@pytest.fixture(name="_dict_list")
def dict_list(clean_csv_dir) -> List[Dict[uuid4, pd.DataFrame]]:
    """Fills a list of dicionaries with uuid4 as keyes and pd.DataFrame as
       values.    
       Returns
        - List[Dict[uuid4,pd.DataFrame]]: Test data
    """
    return [{uuid4(): pd.read_csv(csv)} for
            csv in Path(clean_csv_dir).glob("*.csv")]


@pytest.fixture(name="df")
def data_frame() -> pd.DataFrame:
    """Fills and returns a test DataFrame.
    """
    data = [
        # ---------- July 2025 ----------
        {"date": "2025-07-01", "description": "Interest Payment",
            "category": "Interest Income",       "amount": 1.25},
        {"date": "2025-07-02", "description": "Electric Co.",
            "category": "Utilities",             "amount": -85.30},
        {"date": "2025-07-03", "description": "Comcast Xfinity",
            "category": "Television",            "amount": -70.00},  # subscription
        {"date": "2025-07-03", "description": "AT&T Wireless",
            "category": "Mobile Phone",          "amount": -60.00},
        {"date": "2025-07-05", "description": "Netflix",
            "category": "Entertainment",         "amount": -15.49},  # subscription
        {"date": "2025-07-06", "description": "Adobe Creative Cloud",
            "category": "Software",              "amount": -20.99},  # subscription
        {"date": "2025-07-07", "description": "Credit Card Payment",
            "category": "Credit Card Payment",   "amount": -200.00},
        {"date": "2025-07-08", "description": "Transfer to Savings",
            "category": "Transfer",              "amount": -500.00},
        {"date": "2025-07-12", "description": "Haircut",
            "category": "Personal",              "amount": -25.00},
        {"date": "2025-07-15", "description": "Payroll",
            "category": "Income",                "amount": 2500.00},
        {"date": "2025-07-20", "description": "Bank Fee",
            "category": "Financial",             "amount": -5.00},

        # ---------- August 2025 ----------
        {"date": "2025-08-01", "description": "Interest Payment",
            "category": "Interest Income",       "amount": 1.20},
        {"date": "2025-08-02", "description": "Electric Co.",
            "category": "Utilities",             "amount": -90.10},
        {"date": "2025-08-03", "description": "Comcast Xfinity",
            "category": "Television",            "amount": -70.00},  # subscription
        {"date": "2025-08-03", "description": "AT&T Wireless",
            "category": "Mobile Phone",          "amount": -60.00},
        {"date": "2025-08-05", "description": "Netflix",
            "category": "Entertainment",         "amount": -15.49},  # subscription
        {"date": "2025-08-06", "description": "Adobe Creative Cloud",
            "category": "Software",              "amount": -20.99},  # subscription
        {"date": "2025-08-07", "description": "Credit Card Payment",
            "category": "Credit Card Payment",   "amount": -200.00},
        {"date": "2025-08-10", "description": "Water Utility",
            "category": "Bills & Utilities",     "amount": -30.00},
        {"date": "2025-08-15", "description": "Payroll",
            "category": "Income",                "amount": 2500.00},

        # ---------- September 2025 ----------
        {"date": "2025-09-01", "description": "Interest Payment",
            "category": "Interest Income",       "amount": 1.30},
        {"date": "2025-09-02", "description": "Electric Co.",
            "category": "Utilities",             "amount": -88.75},
        {"date": "2025-09-03", "description": "Comcast Xfinity",
            "category": "Television",            "amount": -70.00},  # subscription
        {"date": "2025-09-03", "description": "AT&T Wireless",
            "category": "Mobile Phone",          "amount": -60.00},
        {"date": "2025-09-05", "description": "Netflix",
            "category": "Entertainment",         "amount": -15.49},  # subscription
        {"date": "2025-09-06", "description": "Adobe Creative Cloud",
            "category": "Software",              "amount": -20.99},  # subscription
        {"date": "2025-09-07", "description": "Credit Card Payment",
            "category": "Credit Card Payment",   "amount": -200.00},
        {"date": "2025-09-08", "description": "Transfer to Savings",
            "category": "Transfer",              "amount": -400.00},
        {"date": "2025-09-15", "description": "Payroll",
            "category": "Income",                "amount": 2500.00},
        {"date": "2025-09-20", "description": "Bank Fee",
            "category": "Financial",             "amount": -5.00},
        {"date": "2025-09-21", "description": "HBO Max",
            "category": "Entertainment",         "amount": -9.99},
    ]

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def test_expense_categories(_dict_list: List[Dict[uuid4, pd.DataFrame]]):
    """Tests the expense catagories method.
       Asserts:
            -categories.dtypes == "float64"
    """
    manager = FinanceManager(data_frame_list=_dict_list)
    categories = manager.expense_categories()
    assert categories.dtypes == "float64"


def test_get_current_month_credit_card_usage(
        _dict_list: List[Dict[uuid4, pd.DataFrame]]):
    """Tests the get_current_month_credit_card_usage
       Asserts:
            -usage.dtypes == np.float64
    """
    record = _dict_list.pop()
    new_record = {"credit": list(record.values()).pop()}
    df = new_record["credit"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    new_record["credit"] = df
    _dict_list.append(new_record)
    manager = FinanceManager(data_frame_list=_dict_list)
    usage = manager.get_current_month_credit_usage()
    assert isinstance(usage, np.float64)


def test_get_subscriptions(df: pd.DataFrame,
                           _dict_list: List[Dict[uuid4, pd.DataFrame]]):
    """Test the get_subscriptions method.
    """
    copy = _dict_list.copy()
    record = copy.pop()
    new_record = {"credit": list(record.values()).pop()}
    copy.clear()
    copy.append(new_record)
    copy.append({"checking": df})
    manager = FinanceManager(data_frame_list=copy)
    subscriptions = manager.get_subscriptions()
    assert set(subscriptions["description"]) == {
        "Comcast Xfinity", "Netflix", "Adobe Creative Cloud"}
