#!/usr/bin/env python3
"""
Скрипт загрузки медицинских данных в PostgreSQL

Использование:
    python load_data.py --data-dir /path/to/csv/files
    
Переменные окружения:
    DATABASE_URL - строка подключения к PostgreSQL
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from typing import List
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Получить DATABASE_URL из окружения"""
    url = os.getenv("DATABASE_URL")
    if not url:
        logger.error("DATABASE_URL не найден в .env")
        logger.info("Пример: DATABASE_URL=postgresql://user:pass@host:5432/dbname")
        sys.exit(1)
    return url


def find_csv_files(data_dir: Path) -> List[Path]:
    """Найти все CSV файлы в директории"""
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        logger.warning(f"CSV файлы не найдены в {data_dir}")
    return csv_files


def load_csv_to_db(csv_path: Path, engine, table_name: str = "disease_cases"):
    """Загрузить CSV в PostgreSQL"""
    logger.info(f"Загружаем {csv_path.name}...")
    
    try:
        # Читаем CSV
        df = pd.read_csv(csv_path)
        logger.info(f"  Прочитано {len(df)} строк")
        
        # Базовая валидация
        required_columns = ['district', 'disease', 'date']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            logger.warning(f"  Пропущены колонки: {missing}")
        
        # Преобразование типов
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Загрузка в БД
        df.to_sql(
            table_name, 
            engine, 
            if_exists='append',  # добавлять к существующим данным
            index=False
        )
        logger.info(f"  ✅ Загружено {len(df)} строк в таблицу {table_name}")
        
    except Exception as e:
        logger.error(f"  ❌ Ошибка при загрузке {csv_path.name}: {e}")
        raise


def verify_data(engine):
    """Проверить что данные загрузились"""
    logger.info("\nПроверка данных...")
    
    with engine.connect() as conn:
        # Общее количество
        result = conn.execute(text("SELECT COUNT(*) FROM disease_cases"))
        total = result.scalar()
        logger.info(f"  Всего записей: {total}")
        
        # Уникальные заболевания
        result = conn.execute(text("SELECT COUNT(DISTINCT disease) FROM disease_cases"))
        diseases = result.scalar()
        logger.info(f"  Уникальных заболеваний: {diseases}")
        
        # Уникальные районы
        result = conn.execute(text("SELECT COUNT(DISTINCT district) FROM disease_cases"))
        districts = result.scalar()
        logger.info(f"  Уникальных районов: {districts}")
        
        # Временной диапазон
        result = conn.execute(text(
            "SELECT MIN(date), MAX(date) FROM disease_cases WHERE date IS NOT NULL"
        ))
        date_range = result.fetchone()
        if date_range:
            logger.info(f"  Период данных: {date_range[0]} — {date_range[1]}")


def main():
    parser = argparse.ArgumentParser(description="Загрузка медицинских данных в PostgreSQL")
    parser.add_argument(
        "--data-dir", 
        type=str, 
        default="../../data/raw",
        help="Путь к директории с CSV файлами"
    )
    args = parser.parse_args()
    
    # Путь к данным
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Директория не найдена: {data_dir}")
        sys.exit(1)
    
    # Подключение к БД
    database_url = get_database_url()
    logger.info(f"Подключение к БД: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    
    engine = create_engine(database_url)
    
    # Проверка подключения
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Подключение успешно\n")
    except Exception as e:
        logger.error(f"❌ Не удалось подключиться к БД: {e}")
        sys.exit(1)
    
    # Найти CSV файлы
    csv_files = find_csv_files(data_dir)
    logger.info(f"Найдено CSV файлов: {len(csv_files)}\n")
    
    # Загрузить каждый файл
    for csv_file in csv_files:
        load_csv_to_db(csv_file, engine)
    
    # Проверка
    verify_data(engine)
    
    logger.info("\n🎉 Данные успешно загружены!")


if __name__ == "__main__":
    main()
