import pandas as pd
from etl.base_processor import BaseProcessor
from typing import List


class DiagnosesProcessor(BaseProcessor):
    """
    Процессор справочника диагнозов.

    Ожидаемая схема:
    - код_мкб
    - название_диагноза
    - класс_заболевания
    """

    def validate(self) -> bool:
        """Строгая проверка схемы."""
        if self.df is None:
            return False

        expected_cols = ["код_мкб", "название_диагноза", "класс_заболевания"]

        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Очистка и переименование."""
        if self.df is None:
            return

        self.logger.info("Стандартизация диагнозов...")

        # 1. Переименование колонок
        rename_map = {
            "код_мкб": "diagnosis_code",
            "название_диагноза": "diagnosis_name",
            "класс_заболевания": "disease_class",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Очистка ключа (Код МКБ)
        self.df["diagnosis_code"] = self.df["diagnosis_code"].astype(str).str.strip().str.upper()

        # 3. Очистка текстовых полей (Класс заболевания)
        self.df["disease_class"] = self.df["disease_class"].astype(str).str.strip()

        # 4. Удаление дубликатов
        self.df = self.df.drop_duplicates(subset=["diagnosis_code"])

        # 5. Удаление дубликатов
        self.remove_duplicates()

    def enrich(self) -> None:
        """Финальная выборка."""
        if self.df is None:
            return

        target_cols = ["diagnosis_code", "diagnosis_name", "disease_class"]

        self.df = self.df[target_cols]
