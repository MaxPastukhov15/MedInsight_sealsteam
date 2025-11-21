# База данных: Пошаговая инструкция

## Что нужно сделать (твоя задача, День 1-2)

### Шаг 1: Установить PostgreSQL на VPS

```bash
# SSH в VPS
ssh user@vps_ip

# Установка PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Проверка
sudo systemctl status postgresql
```

### Шаг 2: Создать базу и пользователя

```bash
# Войти в PostgreSQL
sudo -u postgres psql

# Создать базу
CREATE DATABASE medical_analytics;

# Создать пользователя
CREATE USER med_user WITH PASSWORD 'your_secure_password';

# Дать права
GRANT ALL PRIVILEGES ON DATABASE medical_analytics TO med_user;

# Выйти
\q
```

### Шаг 3: Настроить удалённый доступ

```bash
# Редактировать postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf

# Найти и изменить:
listen_addresses = '*'  # было 'localhost'

# Редактировать pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Добавить в конец:
host    all             all             0.0.0.0/0               md5

# Перезапустить PostgreSQL
sudo systemctl restart postgresql
```

### Шаг 4: Создать таблицу

```bash
# Подключиться
psql -h vps_ip -U med_user -d medical_analytics

# Выполнить SQL
CREATE TABLE disease_cases (
    id SERIAL PRIMARY KEY,
    district VARCHAR(100),
    disease VARCHAR(100),
    date DATE,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Создать индексы (для скорости)
CREATE INDEX idx_disease ON disease_cases(disease);
CREATE INDEX idx_date ON disease_cases(date);
CREATE INDEX idx_district ON disease_cases(district);

# Проверить
\dt
```

### Шаг 5: Загрузить данные

```bash
# На своём компьютере
cd preparing/backend/scripts

# Настроить подключение в .env
DATABASE_URL=postgresql://med_user:your_password@vps_ip:5432/medical_analytics

# Запустить скрипт загрузки
python load_data.py

# Проверить что данные загрузились
psql -h vps_ip -U med_user -d medical_analytics -c "SELECT COUNT(*) FROM disease_cases;"
```

## Если что-то не работает

### Проблема: не подключается удалённо
```bash
# Проверить firewall
sudo ufw allow 5432/tcp

# Проверить что PostgreSQL слушает
sudo netstat -plnt | grep 5432
```

### Проблема: мало памяти (1GB RAM)
```bash
# Оптимизировать PostgreSQL для слабого VPS
sudo nano /etc/postgresql/14/main/postgresql.conf

# Изменить:
shared_buffers = 128MB          # было 256MB
effective_cache_size = 256MB    # было 512MB
work_mem = 4MB                  # было 8MB
maintenance_work_mem = 32MB     # было 64MB

# Перезапустить
sudo systemctl restart postgresql
```

## Для Макса: как подключиться из FastAPI

```python
# backend/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Credentials для команды

После настройки, дай команде:
```
DATABASE_URL=postgresql://med_user:your_password@vps_ip:5432/medical_analytics
```

Все добавят в свой `.env` файл.
