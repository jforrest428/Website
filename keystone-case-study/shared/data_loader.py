"""
Load and serve the Keystone Plumbing sample dataset.

Usage:
    from shared.data_loader import jobs, reviews, customers, ...
"""

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

# Resolve data path: env override > default relative path
_DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "Keystone_Plumbing_Sample_Dataset.xlsx"
DATA_PATH = Path(os.getenv("DATA_PATH", _DEFAULT_DATA_PATH))


@lru_cache(maxsize=1)
def _load_raw() -> dict[str, pd.DataFrame]:
    """Load all sheets once and cache in memory."""
    xl = pd.ExcelFile(DATA_PATH)
    return {sheet: xl.parse(sheet) for sheet in xl.sheet_names}


def customers() -> pd.DataFrame:
    df = _load_raw()["Customers"].copy()
    df["Created"] = pd.to_datetime(df["Created"], errors="coerce")
    return df


def jobs() -> pd.DataFrame:
    df = _load_raw()["Jobs"].copy()
    df["Scheduled"] = pd.to_datetime(df["Scheduled"], errors="coerce")
    df["Completed"] = pd.to_datetime(df["Completed"], errors="coerce")
    return df


def invoices() -> pd.DataFrame:
    df = _load_raw()["Invoices"].copy()
    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], errors="coerce")
    df["Paid Date"] = pd.to_datetime(df["Paid Date"], errors="coerce")
    return df


def calls() -> pd.DataFrame:
    df = _load_raw()["Calls"].copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    return df


def reviews() -> pd.DataFrame:
    df = _load_raw()["Reviews"].copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def technicians() -> pd.DataFrame:
    return _load_raw()["Technicians"].copy()


def parts_inventory() -> pd.DataFrame:
    return _load_raw()["Parts Inventory"].copy()


def summary_kpis() -> pd.DataFrame:
    return _load_raw()["Summary KPIs"].copy()


def latest_job_date() -> pd.Timestamp:
    """Return the most recent date any job was scheduled in the dataset."""
    return jobs()["Scheduled"].max().normalize()


def customer_job_history(customer_id: str) -> pd.DataFrame:
    """Return all jobs for a given customer, sorted by scheduled date."""
    j = jobs()
    return j[j["Customer ID"] == customer_id].sort_values("Scheduled")


def customer_lifetime_revenue(customer_id: str) -> float:
    """Return total revenue earned from a customer across all completed jobs."""
    j = jobs()
    return float(
        j[(j["Customer ID"] == customer_id) & (j["Status"] == "Completed")]["Revenue"]
        .sum()
    )
