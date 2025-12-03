import pandas as pd
import numpy as np
from datetime import datetime
from etl.base_processor import BaseProcessor
from typing import List


class PatientsIntProcessor(BaseProcessor):
    """
    Main patients table processor (Integer ID).

    Transformation schema:
    - id_пациента -> patient_id (str)
    - дата_рождения -> birth_dt (datetime)
      -> age (int)
    - пол -> gender (str)
    - район_проживания -> district (str)
    - регион -> region (str)

    Processing logic:
    - Full duplicates are removed.
    - ID collisions (different data) -> suffix "_N".
    - gender, district, region: Missing -> "UNKNOWN".
    - birth_dt: Missing/Errors -> NaT.
    - age: <0 or >110 -> 0.
    """

    def validate(self) -> bool:
        """Strict schema validation."""
        if self.df is None:
            return False

        expected_cols = ["id_пациента", "дата_рождения", "пол", "район_проживания", "регион"]
        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Cleaning and renaming."""
        if self.df is None:
            return

        self.logger.info("Стандартизация данных...")

        # 1. Renaming columns
        rename_map = {
            "id_пациента": "patient_id",
            "дата_рождения": "birth_date_raw",
            "пол": "gender",
            "район_проживания": "district",
            "регион": "region",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. ID cleaning
        self.df = self.df.dropna(subset=["patient_id"])
        self.df["patient_id"] = self.df["patient_id"].astype(int).astype(str)

        # 3. Geography
        # Fill missing values with 'Unknown', convert to uppercase
        geo_cols = ["district", "region"]
        for col in geo_cols:
            self.df[col] = self.df[col].fillna("Unknown").astype(str).str.strip().str.upper()

        # 4. Gender
        self.df["gender"] = self.df["gender"].fillna("Unknown").astype(str).str.strip().str.upper()

        # 5. Removing duplicates and filling missing values
        self.remove_duplicates()
        self.fill_text_na(["district", "region", "gender"])

    def enrich(self) -> None:
        """Calculation of derived metrics."""
        if self.df is None:
            return

        self.logger.info("Расчет возраста...")

        # 1. Date parsing
        self.df["birth_dt"] = pd.to_datetime(self.df["birth_date_raw"], dayfirst=True, errors="coerce")

        # 2. Check for broken dates
        invalid_dates = self.df["birth_dt"].isna().sum()
        if invalid_dates > 0:
            self.logger.warning(f"Не удалось распознать дату рождения у {invalid_dates} пациентов")

        # 3. Exact age
        now = datetime.now()
        self.df["age"] = (now - self.df["birth_dt"]) / pd.Timedelta(days=365.25)
        self.df["age"] = self.df["age"].fillna(0).astype(int)

        # 4. Outlier filtering
        mask_invalid = (self.df["age"] < 0) | (self.df["age"] > 110)
        if mask_invalid.any():
            self.df.loc[mask_invalid, "age"] = np.nan

        # 5. Final selection
        self.df = self.df[["patient_id", "birth_dt", "age", "gender", "district", "region"]]
