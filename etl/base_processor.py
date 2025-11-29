import pandas as pd
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# Настройка логгера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """
    Базовый класс для ETL процессоров.
    Определяет общий интерфейс и логику pipeline.
    """

    def __init__(self, input_path: str):
        self.input_path = input_path
        self.df: Optional[pd.DataFrame] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def load(self) -> pd.DataFrame:
        """Загрузка данных из CSV"""
        self.logger.info(f"Загрузка файла: {self.input_path}")
        try:
            self.df = pd.read_csv(self.input_path)
            self.logger.info(f"Загружено строк: {len(self.df)}")
            return self.df
        except Exception as e:
            self.logger.error(f"Ошибка загрузки {self.input_path}: {e}")
            raise

    @abstractmethod
    def validate(self) -> bool:
        """
        Валидация данных (проверка структуры, критичных пропусков).
        Должна быть реализована в подклассах.
        """
        pass

    @abstractmethod
    def clean(self) -> None:
        """
        Очистка данных (типы, пропуски, дубликаты).
        Должна быть реализована в подклассах.
        """
        pass

    def enrich(self) -> None:
        """
        Обогащение данных (расчет новых признаков).
        Опциональный шаг.
        """
        pass

    def save(self, output_path: str) -> None:
        """Сохранение результата в Parquet"""
        if self.df is None:
            self.logger.warning("Нет данных для сохранения")
            return

        self.logger.info(f"Сохранение результата в: {output_path}")
        self.df.to_parquet(output_path, index=False)
        self.logger.info("Успешно сохранено")

    def process(self, output_path: str) -> pd.DataFrame:
        """
        Главный метод запуска пайплайна.
        """
        self.logger.info("=== Начало обработки ===")

        self.load()

        if not self.validate():
            raise ValueError("Валидация не пройдена (см. логи)")

        self.clean()
        self.enrich()
        self.save(output_path)

        self.logger.info("=== Обработка завершена ===\n")
        return self.df

    def remove_duplicates(self, subset: Optional[List[str]] = None) -> None:
        """
        Удаляет полные дубликаты строк.
        :param subset: Список колонок для проверки (если None - проверяем всю строку целиком).
        """
        if self.df is None:  #          в работе...
            return

        start_len = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep="first")
        end_len = len(self.df)

        diff = start_len - end_len
        if diff > 0:
            self.logger.info(f"Удалено дубликатов: {diff} (Subset: {subset if subset else 'ALL columns'})")

    def fill_na(self, defaults: Dict[str, Any]) -> None:
        """
        Заполняет пропуски в указанных колонках заданными значениями.
        Пример: {'price': 0.0, 'name': 'Unknown'}f
        """
        if self.df is None:
            return

        for col, value in defaults.items():
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(value)
            else:
                self.logger.warning(f"Попытка заполнить пропуски в несуществующей колонке: {col}")

    def fill_text_na(self, cols: List[str], value: str = "UNKNOWN") -> None:
        """
        Заполняет пропуски в текстовых колонках значением (по дефолту 'UNKNOWN').
        """
        if self.df is None:
            return

        defaults = {col: value for col in cols}
        self.fill_na(defaults)
