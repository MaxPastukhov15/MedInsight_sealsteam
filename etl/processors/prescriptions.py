import pandas as pd
from etl.base_processor import BaseProcessor
from typing import List


class PrescriptionsProcessor(BaseProcessor):
    """
    Процессор таблицы рецептов.

    Ожидаемая схема:
    - id_пациента -> prescription_id
    - дата_рецепта -> date
    - код_диагноза -> diagnosis_code
    - код_препарата -> drug_id
    - id_пациента -> patient_id
                    ->"date"
                    ->year
                    ->month

    1-ая колонка на самом деле id_рецепта
    """

    def validate(self) -> bool:
        """Строгая проверка схемы (4 основные колонки)."""
        if self.df is None:
            return False

        expected_cols = ["id_пациента", "дата_рецепта", "код_диагноза", "код_препарата", "id_пациента.1"]

        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Очистка и переименование."""
        if self.df is None:
            return

        self.logger.info("Стандартизация рецептов...")

        # 1. Переименование колонок
        rename_map = {
            "id_пациента": "prescription_id",
            "id_пациента.1": "patient_id",
            "дата_рецепта": "date_raw",
            "код_диагноза": "diagnosis_code",
            "код_препарата": "drug_id",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Очистка ID (приводим к строкам)
        self.df["prescription_id"].astype(str).str.strip()
        self.df["patient_id"] = self.df["patient_id"].astype(str).str.split(".").str[0].str.strip()

        # 3. Парсинг даты
        self.df["date"] = pd.to_datetime(self.df["date_raw"], errors="coerce", dayfirst=False)
        self.df = self.df.dropna(subset=["date"])

        # 4. Очистка внешних ключей
        self.df["diagnosis_code"] = self.df["diagnosis_code"].astype(str).str.strip().str.upper()
        self.df["drug_id"] = self.df["drug_id"].astype(str).str.strip()

        # 5. Удаление дубликатов
        self.remove_duplicates()

    def enrich(self) -> None:
        """Добавление временных меток."""
        if self.df is None:
            return

        # 1. Компоненты даты
        self.df["year"] = self.df["date"].dt.year
        self.df["month"] = self.df["date"].dt.month

        # 2. Финальная выборка
        target_cols = ["prescription_id", "patient_id", "diagnosis_code", "drug_id", "date", "year", "month"]

        self.df = self.df[target_cols]
