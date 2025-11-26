import pandas as pd
from etl.base_processor import BaseProcessor


class PrescriptionsProcessor(BaseProcessor):
    """
    Процессор таблицы рецептов.

    Ожидаемая схема:
    - id_пациента (Col 1) -> patient_id
    - дата_рецепта -> date
    - код_диагноза -> diagnosis_code
    - код_препарата -> drug_id

    5-ую колонку игнорируем как мусорные данные
    """

    def validate(self) -> bool:
        """Строгая проверка схемы (4 основные колонки)."""
        if self.df is None:
            return False

        expected_cols = ["id_пациента", "дата_рецепта", "код_диагноза", "код_препарата"]

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
            "id_пациента": "patient_id",
            "дата_рецепта": "date_raw",
            "код_диагноза": "diagnosis_code",
            "код_препарата": "drug_id",
        }
        self.df = self.df.rename(columns=rename_map)

        # 2. Очистка (берем первую колонку, которая теперь patient_id)
        self.df["patient_id"] = self.df["patient_id"].astype(str).str.split(".").str[0].str.strip()

        # 3. Парсинг даты
        self.df["date"] = pd.to_datetime(self.df["date_raw"], errors="coerce", dayfirst=False)
        self.df = self.df.dropna(subset=["date"])

        # 4. Очистка внешних ключей
        self.df["diagnosis_code"] = self.df["diagnosis_code"].astype(str).str.strip().str.upper()
        self.df["drug_id"] = self.df["drug_id"].astype(str).str.strip()

    def enrich(self) -> None:
        """Добавление временных меток."""
        if self.df is None:
            return

        # 1. Компоненты даты
        self.df["year"] = self.df["date"].dt.year
        self.df["month"] = self.df["date"].dt.month

        # 2. Финальная выборка (только полезные колонки)
        target_cols = ["patient_id", "diagnosis_code", "drug_id", "date", "year", "month"]

        self.df = self.df[target_cols]
