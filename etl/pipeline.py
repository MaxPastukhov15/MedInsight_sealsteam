import os
import logging
from typing import List, Tuple, Type
from etl.base_processor import BaseProcessor
from etl.processors.patients import PatientsIntProcessor
from etl.processors.diagnoses import DiagnosesProcessor
from etl.processors.medications import MedicationsProcessor
from etl.processors.prescriptions import PrescriptionsProcessor
# from etl.processors.patients_uuid import PatientsUuidProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(raw_dir: str, processed_dir: str) -> None:
    os.makedirs(processed_dir, exist_ok=True)

    # Конфигурация: (Класс, Входной файл, Выходной файл)
    tasks: List[Tuple[Type[BaseProcessor], str, str]] = [
        (PatientsIntProcessor, "patients.csv", "patients.parquet"),
        (DiagnosesProcessor, "diagnoses.csv", "diagnoses.parquet"),
        (MedicationsProcessor, "medications.csv", "medications.parquet"),
        (PrescriptionsProcessor, "prescriptions.csv", "prescriptions.parquet"),
        # (PatientsUuidProcessor, "patients_uuid.csv", "patients_uuid.parquet"),
    ]

    logger.info(f"Запуск Pipeline. Raw: {raw_dir} -> Processed: {processed_dir}")

    for ProcessorClass, input_name, output_name in tasks:
        input_path = os.path.join(raw_dir, input_name)
        output_path = os.path.join(processed_dir, output_name)

        if not os.path.exists(input_path):
            logger.warning(f"Пропущен файл: {input_name} (не найден)")
            continue

        try:
            logger.info(f"Обработка: {input_name}...")
            processor = ProcessorClass(input_path)
            processor.process(output_path)
        except Exception as e:
            logger.error(f"Сбой обработки {input_name}: {e}", exc_info=True)

    logger.info("Pipeline завершен.")


if __name__ == "__main__":
    # Запуск по умолчанию (можно переопределить переменными окружения)
    run_pipeline(os.getenv("RAW_DATA", "data/raw"), os.getenv("PROCESSED_DATA", "data/processed"))
