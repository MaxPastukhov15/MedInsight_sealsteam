import pytest
import pandas as pd
import numpy as np
from etl.processors.prescriptions import PrescriptionsProcessor


@pytest.fixture
def raw_prescriptions_df():
    """
    Грязный датасет рецептов.
    Сценарии по строкам (индексам):
    0. rec_1: Идеальная строка -> ОСТАЕТСЯ.
    1. rec_2: Битая дата (bad-date) -> ОСТАЕТСЯ (дата NaT).
    2. rec_3: Float ID пациента (400.0) -> ОСТАЕТСЯ (становится '400').
    3. rec_4: Пропуски в кодах -> ОСТАЕТСЯ (коды UNKNOWN).
    4. (Пустой): Пустой ID рецепта -> УДАЛЯЕТСЯ.
    5. rec_trash: Пустой ID пациента -> УДАЛЯЕТСЯ.
    """
    data = {
        # 1-я колонка: ID Рецепта
        "id_пациента": ["rec_1", "rec_2", "rec_3", "rec_4", "", "rec_trash"],
        "дата_рецепта": ["2023-01-01", "bad-date", "2023-05-05", "2023-01-01", "2023-01-01", "2023-01-01"],
        "код_диагноза": ["A01", "A01", "A01", None, "A01", "A01"],
        "код_препарата": ["DRUG1", "DRUG1", "DRUG1", None, "DRUG1", "DRUG1"],
        "id_пациента.1": ["100", "200", "400.0", "500", "600", ""],
    }
    return pd.DataFrame(data)


def test_validate_structure_fail():
    """Проверка валидации: отсутствие обязательных колонок."""
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = pd.DataFrame({"col": []})

    assert proc.validate() is False


def test_clean_filtering_and_logic(raw_prescriptions_df):
    """
    Проверка логики очистки:
    1. Удаление строк с пустыми ID.
    2. Сохранение строк с битыми датами (NaT).
    3. Исправление формата ID (float string -> int string).
    4. Заполнение пропусков (UNKNOWN).
    """
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = raw_prescriptions_df.copy()

    proc.clean()

    assert len(proc.df) == 4
    assert "" not in proc.df["prescription_id"].values

    row_2 = proc.df[proc.df["prescription_id"] == "rec_2"].iloc[0]
    assert pd.isna(row_2["date"])

    row_3 = proc.df[proc.df["prescription_id"] == "rec_3"].iloc[0]
    assert row_3["patient_id"] == "400"
    assert "." not in row_3["patient_id"]

    row_4 = proc.df[proc.df["prescription_id"] == "rec_4"].iloc[0]
    assert row_4["diagnosis_code"] == "UNKNOWN"
    assert row_4["drug_id"] == "UNKNOWN"


def test_clean_text_formatting():
    """Проверка форматирования текста (upper, strip)."""
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = pd.DataFrame(
        {
            "id_пациента": ["rec_1"],
            "дата_рецепта": ["2023-01-01"],
            "код_диагноза": [" a01 "],
            "код_препарата": [" drug "],
            "id_пациента.1": ["100"],
        }
    )

    proc.clean()

    assert proc.df.iloc[0]["diagnosis_code"] == "A01"
    assert proc.df.iloc[0]["drug_id"] == "drug"


def test_enrich_dates():
    """Проверка генерации дополнительных колонок (year, month)."""
    proc = PrescriptionsProcessor("dummy.csv")
    proc.df = pd.DataFrame(
        {
            "id_пациента": ["rec_1"],
            "дата_рецепта": ["2023-12-31"],
            "код_диагноза": ["A"],
            "код_препарата": ["B"],
            "id_пациента.1": ["1"],
        }
    )

    proc.clean()
    proc.enrich()

    assert "year" in proc.df.columns
    assert "month" in proc.df.columns
    assert proc.df.iloc[0]["year"] == 2023
    assert proc.df.iloc[0]["month"] == 12
