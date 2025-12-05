# Data Analysis

Exploratory data analysis and analytics modules for medical data.

## Dataset

Source: https://disk.yandex.ru/d/EYdH6iSdrrCCUQ

## Data Schema

```mermaid
erDiagram
    patients ||--o{ prescriptions : ""
    medications ||--o{ prescriptions : ""
    diagnoses ||--o{ prescriptions : ""

    patients {
        VARCHAR patient_id PK
        TIMESTAMP_NS birth_dt
        DOUBLE age
        VARCHAR gender
        VARCHAR district
        VARCHAR region
    }

    medications {
        VARCHAR drug_id PK
        VARCHAR trade_name
        VARCHAR full_name
        VARCHAR dosage
        DOUBLE price
    }

    diagnoses {
        VARCHAR diagnosis_code PK
        VARCHAR diagnosis_name
        VARCHAR disease_class
    }

    prescriptions {
        VARCHAR prescription_id PK
        VARCHAR patient_id FK
        VARCHAR diagnosis_code FK
        VARCHAR drug_id FK
        TIMESTAMP_NS date
        DOUBLE year
        DOUBLE month
    }
```

## Structure

- `analyse/` - Analytics modules
- `notebooks/` - Jupyter notebooks for exploratory analysis
- `tests/` - Unit tests
