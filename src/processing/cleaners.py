"""The cleaners module contains a class for cleaning and normalized csv data.
"""
from pathlib import Path
from typing import List, Dict
import pandas as pd
from config import normalization_config, load_description_category_map


class CSVDataCleaner:
    """Cleans and normalizes incoming CSV finance data."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._columns_map = normalization_config["columns_map"]
        self._drop_list = normalization_config["drop_list"]

    def load_and_clean(self) -> List[dict]:
        """Load and clean all CSV files in a directory.

        Returns:
            list: {account_type: cleaned DataFrame}
        """
        if not self.path.is_dir():
            raise ValueError(f"{self.path} is not a directory")

        cleaned = []
        for file in self.path.glob("*.csv"):
            record = {}
            df = pd.read_csv(file)
            key = "credit" if "Transaction Date" in df.columns else "checking"
            df = self._clean_dataframe(df)
            record[key] = df
            cleaned.append(record)
        return cleaned

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning rules to a single DataFrame."""
        if "Type" in df.columns:
            df = df[df["Type"] == "Sale"]
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        if "Amount" in df.columns:
            df.loc[:, "Amount"] = pd.to_numeric(
                df["Amount"], errors="coerce").fillna(0)
        for col in self._drop_list:
            if col in df.columns:
                df = df.drop(columns=[col])
        df = df.rename(columns=self._columns_map)
        df = CSVDataCleaner.apply_category_mapping(
            df, mapping=load_description_category_map())
        return df.iloc[:, 0:4]

    @staticmethod
    def apply_category_mapping(
        df: pd.DataFrame,
        mapping: Dict[str, str],
        *,
        source_col: str = "description",
        target_col: str = "category",
        default_label: str = "Uncategorized",
        case_insensitive: bool = True,
    ) -> pd.DataFrame:
        """
        1) Create a 'matched' column from exact matches of description -> category.
        2) Set target_col to matched where available.
        3) Fill any remaining NaNs in target_col with default_label.
        """
        out = df.copy()

        # Normalize the source text for comparison
        src = out[source_col].astype(str).str.strip()
        if case_insensitive:
            key_series = src.str.lower()
            norm_map = {str(k).strip().lower(): v for k, v in mapping.items()}
        else:
            key_series = src
            norm_map = {str(k).strip(): v for k, v in mapping.items()}

        # (1) exact match lookup -> 'matched'
        out["matched"] = key_series.map(norm_map)

        # Ensure target column exists
        if target_col not in out.columns:
            out[target_col] = pd.Series(index=out.index, dtype="object")

        # (2) set category where we got a match
        has_match = out["matched"].notna()
        out.loc[has_match, target_col] = out.loc[has_match, "matched"]
        # (3) fill NaNs or empty strings with default_label
        out[target_col] = out[target_col].fillna(
            default_label).replace("", default_label)
        out.drop(columns=["matched"], inplace=True)
        return out


if __name__ == "__main__":
    pass
