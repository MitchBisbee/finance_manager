"""A testing module for the cleaner module.
"""
import pytest
import pandas as pd
from processing.cleaners import CSVDataCleaner


@pytest.fixture()
def category_df():
    return pd.DataFrame({
        "description": ["Netflix", "COMCAST XFINITY", "Random Vendor"],
        "category":   ["", "", ""]
    })


def test_load_and_clean_directory(messy_csv_dir, norm_config):
    """Tests load_and_clean_directory by checking for correct headers and 
       data types. 
    Asserts:
        - isinstance(cleaned_list, list)
        - len(cleaned_list) == 2`
        - "date" in df.columns
        - "description" in df.columns
        - "category" in df.columns
        - "amount" in df.columns
    """
    cleaner = CSVDataCleaner(path=messy_csv_dir)
    cleaner.config = norm_config

    cleaned_list = cleaner.load_and_clean()
    assert isinstance(cleaned_list, list)
    assert len(cleaned_list) == 2

    for d in cleaned_list:
        for df in d.values():
            assert "date" in df.columns
            assert "description" in df.columns
            assert "category" in df.columns
            assert "amount" in df.columns


def test_apply_category_mapping_exact(category_df):
    """Tests the apply_category_mapping_exact method

    Asserts:
        - `out.loc[0, "category"] == "Entertainment"`
        - `out.loc[1, "category"] == "Television"`
    """
    mapping = {"Netflix": "Entertainment", "Comcast Xfinity": "Television"}
    out = CSVDataCleaner.apply_category_mapping(
        category_df, mapping=mapping)
    assert out.loc[0, "category"] == "Entertainment"
    assert out.loc[1, "category"] == "Television"
