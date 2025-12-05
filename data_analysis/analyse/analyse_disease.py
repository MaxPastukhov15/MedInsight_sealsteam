import os
import pandas as pd
import json
import re

def normalize_id(series):
    """
    Robustly converts an ID series to a clean string format for merging.
    Handles integers, floats (123.0 -> "123"), and strings with whitespace.
    """
    s = series.astype(str).str.strip()
    s = s.str.replace(r'\.0$', '', regex=True)
    return s


def clean_filename(s):
    """
    Sanitizes a string to be safe for filenames (removes special chars).
    """

    s = str(s).replace(" ", "_")
    return re.sub(r'(?u)[^-\w.]', '', s)

def load_data():
    """
    Loads the 4 required parquet files from the specified directory.
    Returns a tuple of DataFrames or raises FileNotFoundError.
    """

    script_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.dirname(os.path.dirname(script_dir))
    base_path = os.path.join(base_dir, "data/processed")

    try:
        diagnoses = pd.read_parquet(os.path.join(base_path, "diagnoses.parquet"))
        prescriptions = pd.read_parquet(os.path.join(base_path, "prescriptions.parquet"))
        patients = pd.read_parquet(os.path.join(base_path, "patients.parquet"))
        medications = pd.read_parquet(os.path.join(base_path, "medications.parquet"))
        return diagnoses, prescriptions, patients, medications
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Could not find data files in '{base_path}': {str(e)}")

def analyse_disease(year: int,
                    diagnoses: pd.DataFrame,
                    prescriptions: pd.DataFrame,
                    patients: pd.DataFrame,
                    disease_code: str = None,
                    disease_name: str = None,
                    district: str = None) -> str:
    """
    Analyzes disease data to produce descriptive statistics.

    Args:
        disease_name (str): The name of the disease (e.g., 'Influenza').
        year (int): The target year for analysis.
        district (str, optional): The district to filter by. Defaults to None.

    Returns:
        str: A JSON string containing the calculated statistics.
    """

    target_codes = []
    display_name = ""

    if disease_code:
        target_codes = [disease_code]
        name_match = diagnoses[diagnoses['diagnosis_code'] == disease_code]
        if not name_match.empty:
            display_name = name_match.iloc[0]['diagnosis_name']
        else:
            display_name = f"Code {disease_code}"

        print(f"   > Analyzing specific code: {disease_code} ({display_name})")

    elif disease_name:
        display_name = disease_name
        target_diagnoses = diagnoses[
            diagnoses['diagnosis_name'].str.contains(disease_name, case=False, na=False, regex=False)
        ]
        if target_diagnoses.empty:
            return json.dumps({"error": f"No diagnosis found for name: {disease_name}"}), "error"

        target_codes = target_diagnoses['diagnosis_code'].unique()
        print(f"   > Name '{disease_name}' matches {len(target_codes)} distinct ICD codes.")

    else:
        return json.dumps({"error": "Must provide either disease_code or disease_name"}), "error"

    # We need the current year for stats, and previous year for Growth Rate
    relevant_years = [year, year - 1]

    mask_disease = prescriptions['diagnosis_code'].isin(target_codes)
    mask_year = prescriptions['year'].isin(relevant_years)

    df_filtered = prescriptions[mask_disease & mask_year].copy()
    df_filtered['patient_id'] = normalize_id(df_filtered['patient_id'])

    cols_to_use = ['patient_id', 'birth_dt', 'gender', 'district']

    # We work on slices/copies to avoid SettingWithCopy warnings on the original DFs
    pat_subset = patients[cols_to_use].copy()
    pat_subset['patient_id'] = normalize_id(pat_subset['patient_id'])

    if district and 'district' in pat_subset.columns:
        pat_subset = pat_subset[pat_subset['district'] == district]

    population_count = len(pat_subset)

    # We use left join to preserve prescription counts even if patient details are missing
    df_merged = pd.merge(df_filtered, pat_subset, on='patient_id', how='left')

    df_merged['birth_dt'] = pd.to_datetime(df_merged['birth_dt'], dayfirst=True, errors='coerce')
    df_merged['age'] = df_merged['year'] - df_merged['birth_dt'].dt.year
    df_merged.loc[(df_merged['age'] < 0) | (df_merged['age'] > 120), 'age'] = None

    if district:
        df_merged = df_merged[df_merged['district'] == district]

    df_current = df_merged[df_merged['year'] == year]
    df_prev = df_merged[df_merged['year'] == (year - 1)]

    # --- CALCULATIONS ---
    total_cases = len(df_current)

    # population_count is an Absolute Value
    if population_count > 0:
        incidence_rate_100k = (total_cases / population_count) * 100000
    else:
        incidence_rate_100k = 0.0

    gender_counts = df_current['gender'].value_counts(normalize=True)
    sex_distribution = {
        "M": round(gender_counts.get('М', 0) * 100, 2),
        "F": round(gender_counts.get('Ж', 0) * 100, 2)
    }

    if not df_current.empty and df_current['age'].notna().any():
        mean_age = float(df_current['age'].mean())
        median_age = float(df_current['age'].median())
    else:
        mean_age = 0.0
        median_age = 0.0

    if pd.isna(mean_age): mean_age = 0.0
    if pd.isna(median_age): median_age = 0.0

    def get_age_group(age):
        if pd.isna(age): return None
        if age <= 17: return '0-17'
        elif age <= 30: return '18-30'
        elif age <= 60: return '31-60'
        else: return '60+'

    if not df_current.empty:
        age_bins = df_current['age'].apply(get_age_group).value_counts(normalize=True) * 100
    else:
        age_bins = pd.Series()

    age_groups = {
        "0-17": round(age_bins.get('0-17', 0.0), 2),
        "18-30": round(age_bins.get('18-30', 0.0), 2),
        "31-60": round(age_bins.get('31-60', 0.0), 2),
        "60+": round(age_bins.get('60+', 0.0), 2)
    }

    top_dist_series = df_current['district'].value_counts().head(5)
    top_districts = [
        {"name": name, "count": int(count)}
        for name, count in top_dist_series.items()
    ]

    count_prev = len(df_prev)
    if count_prev > 0:
        growth_rate = ((total_cases - count_prev) / count_prev) * 100
    else:
        growth_rate = 0.0 if total_cases == 0 else 100.0

    file_identifier = disease_code if disease_code else display_name
    file_identifier = clean_filename(file_identifier)

    result = {
        "meta": {
            "analysis_year": year,
            "disease_target": display_name,
            "target_type": "code" if disease_code else "name_search",
            "district_filter": district if district else "All"
        },
        "total_cases": int(total_cases),
        "incidence_per_100k": round(incidence_rate_100k, 2),
        "growth_rate_percent": round(growth_rate, 2),
        "demographics": {
            "sex_distribution": sex_distribution,
            "age_stats": {
                "mean": round(mean_age, 2),
                "median": round(median_age, 2)
            },
            "age_groups": age_groups
        },
        "top_districts": top_districts
    }

    return json.dumps(result, ensure_ascii=False, indent=4), file_identifier