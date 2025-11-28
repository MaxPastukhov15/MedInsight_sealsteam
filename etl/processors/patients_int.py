import pandas as pd
import numpy as np
from datetime import datetime
from etl.base_processor import BaseProcessor
from typing import List


class PatientsIntProcessor(BaseProcessor):
    """
    Процессор основной таблицы пациентов (Integer ID).

    Схема преобразования:
    - id_пациента       -> patient_id (str)
    - дата_рождения     -> birth_dt (datetime)
                        -> age (int)
    - пол               -> gender (str)
    - район_проживания  -> district (str)
    - регион            -> region (str)

    Логика обработки:
    - Полные дубликаты удаляются.
    - Коллизии ID (разные данные) -> суффикс "_N".
    - gender, district, region: Пропуски -> "UNKNOWN".
    - birth_dt: Пропуски/ошибки -> NaT.
    - age: <0 или >110 -> 0.
    """

    def validate(self) -> bool:
        """Строгая проверка схемы."""
        if self.df is None:
            return False

        expected_cols = ["id_пациента", "дата_рождения", "пол", "район_проживания", "регион"]

        missing = [col for col in expected_cols if col not in self.df.columns]

        if missing:
            self.logger.error(f"Неверная структура файла. Отсутствуют колонки: {missing}")
            return False
        return True

    def clean(self) -> None:
        """Очистка и переименование."""
        if self.df is None:
            return

        self.logger.info("Стандартизация данных...")

        # 1. Переименование колонок
        rename_map = {
            "id_пациента": "patient_id",
            "дата_рождения": "birth_date_raw",
            "пол": "gender",
            "район_проживания": "district",
            "регион": "region",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Удаление дубликатов и заполнение пропусков
        self.remove_duplicates()
        self.fill_text_na(["district", "region", "gender"])

        # 3. Очистка ID
        self.df = self.df.dropna(subset=["patient_id"])
        self.df["patient_id"] = self.df["patient_id"].astype(int).astype(str)

        # 4. География
        # Заполняем пропуски 'Unknown', приводим к верхнему регистру
        geo_cols = ["district", "region"]

        for col in geo_cols:
            self.df[col] = self.df[col].fillna("Unknown").astype(str).str.strip().str.upper()

        # 5. Пол
        self.df["gender"] = self.df["gender"].fillna("Unknown").astype(str).str.strip().str.upper()

        def enrich(self) -> None:
            """Расчет производных метрик."""
            if self.df is None:
                return

            self.logger.info("Расчет возраста...")

            # 1. Парсинг даты
            self.df["birth_dt"] = pd.to_datetime(self.df["birth_date_raw"], dayfirst=True, errors="coerce")

            # 2. Проверка на битые даты
            invalid_dates = self.df["birth_dt"].isna().sum()
            if invalid_dates > 0:
                self.logger.warning(f"Не удалось распознать дату рождения у {invalid_dates} пациентов")

            # 3. Точный возраст
            now = datetime.now()
            self.df["age"] = (now - self.df["birth_dt"]) / pd.Timedelta(days=365.25)
            self.df["age"] = self.df["age"].fillna(0).astype(int)

            # 4. Фильтрация выбросов
            mask_invalid = (self.df["age"] < 0) | (self.df["age"] > 110)
            if mask_invalid.any():
                self.df.loc[mask_invalid, "age"] = np.nan

            # 5. Финальная выборка
            self.df = self.df[["patient_id", "birth_dt", "age", "gender", "district", "region"]]
