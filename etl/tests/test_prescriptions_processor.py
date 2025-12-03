import pytest
import pandas as pd
import numpy as np
from etl.processors.prescriptions import PrescriptionsProcessor


@pytest.fixture
def raw_prescriptions_df():
    """
    Dirty prescriptions dataset.
    Scenarios by rows (indices):
    0. rec_1: Ideal row -> KEPT.
    1. rec_2: Broken date (bad-date) -> KEPT (date is NaT).
    2. rec_3: Float Patient ID (400.0) -> KEPT (becomes '400').
    3. rec_4: Missing codes -> KEPT (codes become UNKNOWN).
    4. (Empty): Empty Prescription ID -> REMOVED.
    5. rec_trash: Empty Patient ID -> REMOVED.
    """
    data = {
        # 1st column: Prescription ID
        "id_пациента": ["rec_1", "rec_2", "rec_3", "rec_4", "", "rec_trash"],
        "дата_рецепта": ["2023-01-01", "bad-date", "2023-05-05", "2023-01-01", "2023-01-01", "2023-01-01"],
        "код_диагноза": ["A01", "A01", "A01", None, "A01", "A01"],
        "код_препарата": ["DRUG1", "DRUG1", "DRUG1", None, "DRUG1", "DRUG1"],
        "id_пациента.1": ["100", "200", "400.0", "500", "600", ""],
    }
    return pd.DataFrame(data)


def test_validate_structure_fail():
    """Validation check: missing mandatory columns."""
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = pd.DataFrame({"col": []})

    assert proc.validate() is False


def test_clean_filtering_and_logic(raw_prescriptions_df):
    """
    Cleaning logic check:
    1. Removal of rows with empty IDs.
    2. Preservation of rows with broken dates (NaT).
    3. ID format correction (float string -> int string).
    4. Filling missing values (UNKNOWN).
    """
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = raw_prescriptions_df.copy()

    proc.clean()

    assert len(proc.df) == 4
    assert "" not in proc.df["prescription_id"].values

    row_2 = proc.df[proc.df["prescription_id"] == "rec_2"].iloc[0]
    assert pd.isna(row_2["date"])

    row_3 = proc.df[proc.df["prescription_id"] == "rec_3"].iloc[0]
    assert row_3["patient_id"] == "400"
    assert "." not in row_3["patient_id"]

    row_4 = proc.df[proc.df["prescription_id"] == "rec_4"].iloc[0]
    assert row_4["diagnosis_code"] == "UNKNOWN"
    assert row_4["drug_id"] == "UNKNOWN"


def test_clean_text_formatting():
    """Text formatting check (upper, strip)."""
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = pd.DataFrame(
        {
            "id_пациента": ["rec_1"],
            "дата_рецепта": ["2023-01-01"],
            "код_диагноза": [" a01 "],
            "код_препарата": [" drug "],
            "id_пациента.1": ["100"],
        }
    )

    proc.clean()

    assert proc.df.iloc[0]["diagnosis_code"] == "A01"
    assert proc.df.iloc[0]["drug_id"] == "drug"


def test_enrich_dates():
    """Additional columns generation check (year, month)."""
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = pd.DataFrame(
        {
            "id_пациента": ["rec_1"],
            "дата_рецепта": ["2023-12-31"],
            "код_диагноза": ["A"],
            "код_препарата": ["B"],
            "id_пациента.1": ["1"],
        }
    )

    proc.clean()
    proc.enrich()

    assert "year" in proc.df.columns
    assert "month" in proc.df.columns
    assert proc.df.iloc[0]["year"] == 2023
    assert proc.df.iloc[0]["month"] == 12
