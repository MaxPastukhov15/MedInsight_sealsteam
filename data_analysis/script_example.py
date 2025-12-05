import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import json
import pandas as pd

from analyse.analyse_disease import analyse_disease, load_data

if __name__ == "__main__":
    try:
        diagnoses, prescriptions, patients, medications = load_data()

        unique_years = sorted(prescriptions['year'].dropna().unique().tolist()) # 2019-2025
        unique_diseases = sorted(diagnoses['diagnosis_name'].dropna().unique().tolist()) # 14678 cases
        unique_districts = sorted(patients['district'].dropna().unique().tolist()) # 28 cases

        # CONFIGURATION SECTION
        target_year = unique_years[-1] if unique_years else 2025

        # OPTION 1: Set a specific code (Prioritized if not None)
        target_code = "I11.9"

        # OPTION 2: Set a disease name
        target_disease_name = "Туберкулез"

        # OPTION 3: Set District
        target_district = None

        if target_code:
            print(f"\nRunning analysis for Code: {target_code} ({target_year})")
            json_result, file_id = analyse_disease(
                year=target_year,
                diagnoses=diagnoses,
                prescriptions=prescriptions,
                patients=patients,
                disease_code=target_code,
                disease_name=None,
                district=target_district
            )
        else:
            print(f"\nRunning analysis for Name: {target_disease_name} ({target_year})")
            json_result, file_id = analyse_disease(
                year=target_year,
                diagnoses=diagnoses,
                prescriptions=prescriptions,
                patients=patients,
                disease_code=None,
                disease_name=target_disease_name,
                district=target_district
            )

        output_filename = f"analysis_result_{file_id}_{target_year}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(json_result)

        print(f"Results saved to '{output_filename}'")
        # print("\n--- JSON Result Preview ---")
        # print(json_result)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
