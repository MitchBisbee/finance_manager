from pathlib import Path
import pandas as pd
import pytest

from config import normalization_config


@pytest.fixture
def norm_config():
    return normalization_config


@pytest.fixture
def messy_csv_dir(tmp_path: Path):
    """Fixture: make a temp dir with messy CSVs, then tear it down."""
    d = tmp_path / "july"
    d.mkdir()

    df1 = pd.DataFrame({
        "Transaction Date": ["2024-07-01", "2024-07-03", "2024-07-05"],
        "Post Date": ["2024-07-02", "2024-07-04", "2024-07-06"],
        "Description": ["Netflix Subscription", "Whole Foods Market", "Uber Ride"],
        "Category": ["Entertainment & Rec.", "Groceries", ""],
        "Type": ["Sale", "Sale", "Payment"],
        "Amount": [-15.99, -82.50, 23.75],
        "Memo": ["Monthly billing", "Grocery shopping", "Ride to airport"]
    })

    df1.to_csv(d / "first.csv", index=False)
    df2 = pd.DataFrame({
        "Date": ["2024-07-10", "2024-07-11", "2024-07-12"],
        "Description": ["Hulu Subscription", "Bank Fee", "Target Purchase"],
        "Original Description": ["Hulu*HULU.COM", "Monthly Service Fee", "TARGET #1234"],
        "Category": ["Entertainment & Rec.", "Fees", "Groceries"],
        "Amount": [-12.99, -5.00, -45.25],
        "Status": ["Posted", "Posted", "Pending"]
    })

    df2.to_csv(d / "second.csv", index=False)

    yield d


@pytest.fixture()
def clean_csv_dir(tmp_path: Path):
    """Fixture: make a temp dir with clean CSVs, then tear it down."""
    d = tmp_path / "july"
    d.mkdir()

    df1 = pd.DataFrame({
        "date": ["2024-07-01", "2024-07-03", "2024-07-05"],
        "description": ["Netflix Subscription", "Whole Foods Market", "Uber Ride"],
        "category": ["Entertainment & Rec.", "Groceries", "Personal"],
        "amount": [-15.99, -82.50, 23.75],
    })

    df1.to_csv(d / "first.csv", index=False)
    df2 = pd.DataFrame({
        "date": ["2024-07-10", "2024-07-11", "2024-07-12"],
        "description": ["Hulu Subscription", "Bank Fee", "Target Purchase"],
        "category": ["Entertainment & Rec.", "Fees", "Groceries"],
        "amount": [-12.99, -5.00, -45.25]
    })

    df2.to_csv(d / "second.csv", index=False)

    yield d
