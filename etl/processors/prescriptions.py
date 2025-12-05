import pandas as pd
from etl.base_processor import BaseProcessor


class PrescriptionsProcessor(BaseProcessor):
    """
    Prescriptions table processor.

    Transformation schema:
    - id_пациента (1st col) -> prescription_id (str)
    - id_пациента (5th col) -> patient_id (str)
    - дата_рецепта -> date (datetime)
                   -> year (int)
                   -> month (int)
    - код_диагноза -> diagnosis_code (str)
    - код_препарата -> drug_id (str)

    Processing logic:
    - 1st column is considered Prescription ID, 5th — Patient ID.
    - diagnosis_code, drug_id -> "UNKNOWN" (if empty).
    - date: Missing/Errors -> NaT.
    - patient_id, prescription_id: Empty values are removed.
    """

    def validate(self) -> bool:
        """Strict schema validation."""
        if self.df is None:
            return False

        expected_cols = ["id_пациента", "дата_рецепта", "код_диагноза", "код_препарата", "id_пациента.1"]
        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Cleaning and renaming."""
        if self.df is None:
            return

        self.logger.info("Стандартизация рецептов...")

        # 1. Renaming columns
        rename_map = {
            "id_пациента": "prescription_id",
            "id_пациента.1": "patient_id",
            "дата_рецепта": "date_raw",
            "код_диагноза": "diagnosis_code",
            "код_препарата": "drug_id",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. ID cleaning (convert to strings)
        self.df["prescription_id"] = self.df["prescription_id"].astype(str).str.strip()
        self.df["patient_id"] = self.df["patient_id"].astype(str).str.split(".").str[0].str.strip()

        mask_valid_presc = ~self.df["prescription_id"].isin(["", "nan", "None"])
        mask_valid_patient = ~self.df["patient_id"].isin(["", "nan", "None"])
        self.df = self.df[mask_valid_presc & mask_valid_patient]

        # 3. Date parsing
        self.df["date"] = pd.to_datetime(self.df["date_raw"], errors="coerce", dayfirst=False)

        # 4. Foreign keys cleaning
        self.df["diagnosis_code"] = self.df["diagnosis_code"].astype(str).str.strip().str.upper()
        self.df["drug_id"] = self.df["drug_id"].astype(str).str.strip()

        # 5. Removing duplicates and filling missing values
        self.remove_duplicates()
        self.fill_text_na(["diagnosis_code", "drug_id"])

    def enrich(self) -> None:
        """Adding temporal features."""
        if self.df is None:
            return

        # 1. Date components
        self.df["year"] = self.df["date"].dt.year
        self.df["month"] = self.df["date"].dt.month

        # 2. Final selection
        target_cols = ["prescription_id", "patient_id", "diagnosis_code", "drug_id", "date", "year", "month"]
        self.df = self.df[target_cols]
