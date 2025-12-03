import pandas as pd
from etl.base_processor import BaseProcessor
from typing import List


class DiagnosesProcessor(BaseProcessor):
    """
    Diagnoses reference processor (ICD).

    Transformation schema:
    - код_мкб -> diagnosis_code (str)
    - название_диагноза -> diagnosis_name (str)
    - класс_заболевания -> disease_class (str)

    Processing logic:
    - diagnosis_name, disease_class: Missing -> "UNKNOWN".
    - diagnosis_code: Converted to uppercase, spaces removed.
    """

    def validate(self) -> bool:
        """Strict schema validation."""
        if self.df is None:
            return False

        expected_cols = ["код_мкб", "название_диагноза", "класс_заболевания"]
        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Cleaning and renaming."""
        if self.df is None:
            return

        self.logger.info("Стандартизация диагнозов...")

        # 1. Renaming columns
        rename_map = {
            "код_мкб": "diagnosis_code",
            "название_диагноза": "diagnosis_name",
            "класс_заболевания": "disease_class",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Key cleaning (ICD Code)
        self.df["diagnosis_code"] = self.df["diagnosis_code"].astype(str).str.strip().str.upper()

        # 3. Text fields cleaning (Disease class)
        self.df["disease_class"] = self.df["disease_class"].astype(str).str.strip()

        # 4. Removing duplicates and filling missing values
        self.remove_duplicates()
        self.fill_text_na(["diagnosis_name", "disease_class"])

    def enrich(self) -> None:
        """Final selection."""
        if self.df is None:
            return

        target_cols = ["diagnosis_code", "diagnosis_name", "disease_class"]
        self.df = self.df[target_cols]
