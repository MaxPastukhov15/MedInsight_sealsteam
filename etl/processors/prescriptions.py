import pandas as pd
from etl.base_processor import BaseProcessor
from typing import List


class PrescriptionsProcessor(BaseProcessor):
    """
    Процессор таблицы рецептов.

    Схема преобразования:
    - id_пациента (1-я кол.) -> prescription_id (str)
    - id_пациента (5-я кол.) -> patient_id (str)
    - дата_рецепта           -> date (datetime)
                             -> year (int)
                             -> month (int)
    - код_диагноза           -> diagnosis_code (str)
    - код_препарата          -> drug_id (str)

    Логика обработки:
    - 1-я колонка считается ID рецепта, 5-я — ID пациента.
    - diagnosis_code, drug_id -> "UNKNOWN" (если пустые).
    - date: Пропуски/ошибки -> NaT.
    - patient_id, prescription_id: Пустые значения удаляются.
    """

    def validate(self) -> bool:
        """Строгая проверка схемы."""
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

        # 2. Удаление дубликатов и заполнение пропусков
        self.remove_duplicates()
        self.fill_text_na(["diagnosis_code", "drug_id"])

        # 3. Очистка ID (приводим к строкам)
        self.df["prescription_id"] = self.df["prescription_id"].astype(str).str.strip()
        self.df["patient_id"] = self.df["patient_id"].astype(str).str.split(".").str[0].str.strip()
        mask_valid_presc = ~self.df["prescription_id"].isin(["", "nan", "None"])
        mask_valid_patient = ~self.df["patient_id"].isin(["", "nan", "None"])

        # 4. Парсинг даты
        self.df["date"] = pd.to_datetime(self.df["date_raw"], errors="coerce", dayfirst=False)
        self.df = self.df.dropna(subset=["date"])

        # 5. Очистка внешних ключей
        self.df["diagnosis_code"] = self.df["diagnosis_code"].astype(str).str.strip().str.upper()
        self.df["drug_id"] = self.df["drug_id"].astype(str).str.strip()

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
