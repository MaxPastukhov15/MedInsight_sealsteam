import pandas as pd
from etl.base_processor import BaseProcessor
from typing import List


class MedicationsProcessor(BaseProcessor):
    """
    Процессор справочника лекарств.

    Схема преобразования:
    - код_препарата     -> drug_id (str)
    - Полное_название   -> full_name (str)
    - Торговое название -> trade_name (str)
    - стоимость         -> price (float)
    - дозировка         -> dosage (str)


    Логика обработки:
    - price: Пропуски -> NaN.
    - full_name, trade_name, dosage: Пропуски -> "UNKNOWN".
    """

    def validate(self) -> bool:
        """Строгая проверка схемы."""
        if self.df is None:
            return False

        expected_cols = ["код_препарата", "дозировка", "Торговое название", "стоимость", "Полное_название"]

        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Очистка и переименование."""
        if self.df is None:
            return

        self.logger.info("Стандартизация справочника лекарств...")

        # 1. Переименование колонок
        rename_map = {
            "код_препарата": "drug_id",
            "дозировка": "dosage",
            "Торговое название": "trade_name",
            "стоимость": "price",
            "Полное_название": "full_name",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Удаление дубликатов и заполнение пропусков
        self.remove_duplicates()
        self.fill_text_na(["full_name", "trade_name", "dosage"])

        # 3. Очистка ID
        self.df["drug_id"] = self.df["drug_id"].astype(str).str.strip()

        # 4. Очистка Цены
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce").fillna(0.0)

        # 5. Текстовые поля (strip)
        text_cols = ["trade_name", "full_name", "dosage"]
        for col in text_cols:
            self.df[col] = self.df[col].astype(str).str.strip()

    def enrich(self) -> None:
        """Финальная выборка."""
        if self.df is None:
            return

        target_cols = ["drug_id", "trade_name", "full_name", "dosage", "price"]

        self.df = self.df[target_cols]
