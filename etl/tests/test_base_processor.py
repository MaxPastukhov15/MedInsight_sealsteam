import pytest
import pandas as pd
import numpy as np
from etl.base_processor import BaseProcessor
from unittest.mock import patch, MagicMock
import logging


class MockProcessor(BaseProcessor):
    """Пустышка для тестирования методов базового класса."""

    def validate(self) -> bool:
        return True

    def clean(self) -> None:
        pass

    def enrich(self) -> None:
        pass


@pytest.fixture
def sample_df():
    """Стандартный грязный датафрейм."""
    data = {"id": [1, 2, 2, 3], "text": ["A", None, "B", np.nan], "val": [10, 20, 20, 30]}
    return pd.DataFrame(data)


@pytest.fixture
def empty_df():
    """Пустой датафрейм для проверки граничных случаев."""
    return pd.DataFrame({"col1": [], "col2": []})


def test_remove_duplicates_full_row(sample_df):
    """Проверка удаления полных дубликатов."""
    proc = MockProcessor("dummy.csv")

    df = pd.DataFrame({"A": [1, 1, 2], "B": ["x", "x", "y"]})
    proc.df = df

    proc.remove_duplicates()

    assert len(proc.df) == 2
    assert proc.df.iloc[0]["A"] == 1
    assert proc.df.iloc[1]["A"] == 2


def test_remove_duplicates_subset(sample_df):
    """Проверка удаления дубликатов по подмножеству колонок (subset)."""
    proc = MockProcessor("dummy.csv")

    df = pd.DataFrame({"A": [1, 1, 2], "B": ["x", "z", "y"]})
    proc.df = df

    proc.remove_duplicates(subset=["A"])

    assert len(proc.df) == 2
    assert proc.df.iloc[0]["B"] == "x"
    assert proc.df.iloc[1]["B"] == "y"


def test_fill_text_na(sample_df):
    """Проверка заполнения пропусков (None и NaN) и работы параметра value."""
    proc = MockProcessor("dummy.csv")
    proc.df = sample_df.copy()

    # Проверяем кастомное значение "EMPTY"
    proc.fill_text_na(["text"], value="EMPTY")

    assert proc.df["text"].isna().sum() == 0
    assert (proc.df["text"] == "EMPTY").sum() == 2
    assert "A" in proc.df["text"].values


def test_fill_na_dict(sample_df):
    """Проверка универсального заполнения и игнорирования чужих колонок."""
    proc = MockProcessor("dummy.csv")
    proc.df = sample_df.copy()

    proc.df.loc[0, "val"] = np.nan
    proc.fill_na({"text": "U", "val": 999, "ghost_col": "fail"})

    assert proc.df.iloc[0]["val"] == 999.0
    assert (proc.df["text"] == "U").any()


def test_methods_on_none_df():
    """Граничный случай: если self.df is None, методы не должны падать."""
    proc = MockProcessor("dummy.csv")
    proc.df = None

    try:
        proc.remove_duplicates()
        proc.fill_na({"a": 1})
        proc.fill_text_na(["a"])
    except Exception as e:
        pytest.fail(f"Методы упали на None DataFrame: {e}")


def test_methods_on_empty_df(empty_df):
    """Граничный случай: пустой DataFrame."""
    proc = MockProcessor("dummy.csv")
    proc.df = empty_df

    proc.remove_duplicates()
    proc.fill_text_na(["col1"])

    assert len(proc.df) == 0


def test_load_csv_success():
    """Тест успешной загрузки CSV."""
    proc = MockProcessor("data/test.csv")

    with patch("pandas.read_csv") as mock_read:
        mock_read.return_value = pd.DataFrame({"col": [1, 2]})

        proc.load()

        assert proc.df is not None
        assert len(proc.df) == 2
        mock_read.assert_called_once_with("data/test.csv")


def test_load_file_not_found():
    """Тест ошибки при загрузке (файл не найден)."""
    proc = MockProcessor("ghost.csv")

    with patch("pandas.read_csv", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            proc.load()


def test_save_parquet_success():
    """Тест сохранения в Parquet."""
    proc = MockProcessor("dummy.csv")
    proc.df = pd.DataFrame({"a": [1]})

    with patch.object(pd.DataFrame, "to_parquet") as mock_save:
        proc.save("output.parquet")

        mock_save.assert_called_once_with("output.parquet", index=False)


def test_process_flow_integration():
    """
    Тест полного цикла: process().
    Проверяем, что вызываются load -> validate -> clean -> enrich -> save.
    """
    proc = MockProcessor("in.csv")

    # Используем MagicMock для подмены методов самого класса
    with patch.object(MockProcessor, "load") as mock_load, patch.object(MockProcessor, "save") as mock_save:
        # Симулируем успешную загрузку
        proc.df = pd.DataFrame({"a": [1]})
        mock_load.side_effect = lambda: setattr(proc, "df", pd.DataFrame({"a": [1]}))

        proc.process("out.parquet")

        assert mock_load.called
        assert mock_save.called


def test_process_stops_on_validation_fail():
    """Тест остановки пайплайна, если валидация не прошла."""
    proc = MockProcessor("in.csv")

    with (
        patch.object(MockProcessor, "load"),
        patch.object(MockProcessor, "validate", return_value=False) as mock_val,
        patch.object(MockProcessor, "save") as mock_save,
    ):
        with pytest.raises(ValueError, match="Валидация не пройдена"):
            proc.process("out.parquet")

        assert mock_val.called
        assert not mock_save.called


def test_save_no_data(caplog):
    """Тест сохранения при df = None."""
    proc = MockProcessor("dummy.csv")
    proc.df = None

    with caplog.at_level(logging.WARNING):
        proc.save("output.parquet")

    assert "Нет данных для сохранения" in caplog.text
