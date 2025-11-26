import pandas as pd
import numpy as np
from datetime import datetime
from etl.base_processor import BaseProcessor


class PatientsUuidProcessor(BaseProcessor):
    """
    Процессор для patients_uuid.csv.

    Ожидаемая схема:
    - id (UUID)
    - дата_рождения
    - пол

    СНИЛС игнорируется как ненужные данные.
    """

    def validate(self) -> bool:
        """Строгая проверка схемы."""
        if self.df is None:
            return False

        expected_cols = ["id", "дата_рождения", "пол"]

        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Очистка и стандартизация под общую схему. Генерация синтетического ID."""
        if self.df is None:
            return

        self.logger.info("Стандартизация данных...")

        # 1. Переименование
        rename_map = {
            "id": "patient_id",  # UUID становится основным ID
            "дата_рождения": "birth_date_raw",
            "пол": "gender",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Генерация синтетического ID
        start_id = 10_000_000
        count = len(self.df)

        new_ids = range(start_id, start_id + count)
        self.df["patient_id"] = new_ids

        self.df["patient_id"] = self.df["patient_id"].astype(str)

        # 3. Очистка пола
        self.df["gender"] = self.df["gender"].fillna("Unknown").astype(str).str.strip().str.upper()

        # 4. Заглушки для географии
        self.df["district"] = "UNKNOWN"
        self.df["region"] = "UNKNOWN"

    def enrich(self) -> None:
        """Расчет возраста (аналогично основному датасету)."""
        if self.df is None:
            return

        # 1. Парсинг даты
        self.df["birth_dt"] = pd.to_datetime(self.df["birth_date_raw"], dayfirst=True, errors="coerce")

        # 2. Возраст
        now = datetime.now()
        self.df["age"] = (now - self.df["birth_dt"]) / pd.Timedelta(days=365.25)
        self.df["age"] = self.df["age"].fillna(0).astype(int)

        # 3. Фильтрация выбросов
        mask_invalid = (self.df["age"] < 0) | (self.df["age"] > 110)
        if mask_invalid.any():
            self.df.loc[mask_invalid, "age"] = np.nan

        # 4. Финальная выборка (схема идентична patients_int)
        self.df = self.df[["patient_id", "birth_dt", "age", "gender", "district", "region"]]
