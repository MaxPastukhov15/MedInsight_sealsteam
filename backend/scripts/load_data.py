#!/usr/bin/env python3
"""Скрипт загрузки CSV в PostgreSQL."""

import argparse
import logging
import os
import sys
from pathlib import Path
# from typing import List  # F401: unused import

import pandas as pd
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.connection import engine
from backend.database.models import Base

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Load CSV data into database."""
    print("🔧 Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")

    # Find CSV files
    data_dir = Path("data/raw")
    if not data_dir.exists():
        print(f"❌ Директория {data_dir} не найдена")
        print("💡 Создайте директорию и положите CSV файлы")
        return

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"❌ CSV файлы не найдены в {data_dir}")
        return

    print(f"\n📁 Найдено {len(csv_files)} CSV файлов\n")

    total_rows = 0
    for csv_file in csv_files:
        print(f"📄 Загружаем {csv_file.name}...")
        try:
            df = pd.read_csv(csv_file)
            print(f"   Прочитано {len(df)} строк")

            # Convert date column
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            # Load to database
            df.to_sql("disease_cases", engine, if_exists="append", index=False)
            total_rows += len(df)
            print(f"   ✅ Загружено {len(df)} строк")

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

    print(f"\n🎉 Всего загружено: {total_rows} строк")

    # Verify
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM disease_cases"))
        count = result.scalar()
        print(f"✅ Проверка: {count} записей в БД")


if __name__ == "__main__":
    main()
