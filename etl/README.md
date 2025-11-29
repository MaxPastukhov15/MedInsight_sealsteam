# ETL Pipeline

Модуль для первичной обработки (Cleaning & Standardization) сырых данных.

## Структура
- `base_processor.py`: Базовый класс с общей логикой.
- `processors/`: Логика очистки конкретных сущностей (Пациенты, Рецепты...).
- `pipeline.py`: Скрипт запуска всего процесса.

## Как запустить

1. Убедитесь, что сырые CSV лежат в `data/raw/`.
   - `diagnoses.csv`
   - `medications.csv`
   - `prescriptions.csv`
   - `patients_uuid.csv`
   - `patients_int.csv`

2. Запустите pipeline из корня проекта:

bash
'''
python -m etl.pipeline
'''

3. Результат появится в `data/processed/` в формате Parquet.
