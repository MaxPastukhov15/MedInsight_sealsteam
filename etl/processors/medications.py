import pandas as pd
from etl.base_processor import BaseProcessor


class MedicationsProcessor(BaseProcessor):
    """
    Medications reference processor.

    Transformation schema:
    - код_препарата -> drug_id (str)
    - Полное_название -> full_name (str)
    - Торговое название -> trade_name (str)
    - стоимость -> price (float)
    - дозировка -> dosage (str)

    Processing logic:
    - price: Missing -> NaN.
    - full_name, trade_name, dosage: Missing -> "UNKNOWN".
    """

    def validate(self) -> bool:
        """Strict schema validation."""
        if self.df is None:
            return False

        expected_cols = ["код_препарата", "дозировка", "Торговое название", "стоимость", "Полное_название"]
        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Cleaning and renaming."""
        if self.df is None:
            return

        self.logger.info("Стандартизация справочника лекарств...")

        # 1. Renaming columns
        rename_map = {
            "код_препарата": "drug_id",
            "дозировка": "dosage",
            "Торговое название": "trade_name",
            "стоимость": "price",
            "Полное_название": "full_name",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. ID cleaning
        self.df["drug_id"] = self.df["drug_id"].astype(str).str.strip()

        # 3. Price cleaning
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")

        # 4. Text fields (strip)
        text_cols = ["trade_name", "full_name", "dosage"]
        for col in text_cols:
            self.df[col] = self.df[col].astype(str).str.strip()

        # 5. Removing duplicates and filling missing values
        self.remove_duplicates()
        self.fill_text_na(["full_name", "trade_name", "dosage"])

    def enrich(self) -> None:
        """Final selection."""
        if self.df is None:
            return

        target_cols = ["drug_id", "trade_name", "full_name", "dosage", "price"]
        self.df = self.df[target_cols]
