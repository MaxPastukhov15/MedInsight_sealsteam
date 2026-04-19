import pandas as pd
import numpy as np
import json
from datetime import datetime
from analyse_disease import load_data, normalize_id


class NpEncoder(json.JSONEncoder):
    """Handles NumPy types for JSON serialization"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.strftime("%Y-%m-%d")
        return super(NpEncoder, self).default(obj)


def get_master_dataframe():
    """
    Loads and merges all tables into one efficient DataFrame for analysis.
    """
    print("Loading data...")
    diagnoses, prescriptions, patients, medications = load_data()

    prescriptions["patient_id"] = normalize_id(prescriptions["patient_id"])
    patients["patient_id"] = normalize_id(patients["patient_id"])

    # use inner join because we can't analyze demographics if patient data is missing
    df = pd.merge(prescriptions, patients, on="patient_id", how="inner")
    df = pd.merge(df, diagnoses, on="diagnosis_code", how="left")

    # Drop rows without valid dates for the time-series analysis (<1% missing)
    df = df.dropna(subset=["date"])

    # creating a 'root_code' (e.g., 'A02') for grouping & filtering
    df["root_code"] = df["diagnosis_code"].astype(str).str[:3]
    root_names = diagnoses[diagnoses["diagnosis_code"].str.len() == 3][["diagnosis_code", "diagnosis_name"]]
    root_map = dict(zip(root_names["diagnosis_code"], root_names["diagnosis_name"]))

    # We are sure that there is not any missing codes and names
    df["root_name"] = df["root_code"].map(root_map)

    df["birth_dt"] = pd.to_datetime(df["birth_dt"], dayfirst=True, errors="coerce")
    df["age"] = df["year"] - df["birth_dt"].dt.year
    df = df[(df["age"] >= 0) & (df["age"] <= 120)]

    return df
