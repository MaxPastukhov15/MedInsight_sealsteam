# Установка и запуск

## Предварительные требования

### Software
- Python 3.11 или выше
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (для фронтенда)
- Docker и Docker Compose (опционально)

## Установка Backend

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Ronshin-Vsevolod/preparing.git
cd preparing
```

### 2. Создать виртуальное окружение

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

### 3. Установить зависимости

```bash
make install-dev
# или вручную
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio pytest-cov mypy black isort flake8 pre-commit
```

### 4. Настроить переменные окружения

```bash
cp backend/.env.example backend/.env
```

Отредактируйте `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/medical_analytics
REDIS_URL=redis://localhost:6379
LLM_PROVIDER=ollama
```

### 5. Запустить БД и Redis

#### Через Docker Compose:

```bash
docker-compose up -d postgres redis
```

#### Или локально:

```bash
# PostgreSQL
sudo systemctl start postgresql
psql -U postgres -c "CREATE DATABASE medical_analytics;"

# Redis
sudo systemctl start redis
```

### 6. Запустить backend

```bash
make run
# или
cd backend && uvicorn main:app --reload
```

API доступен на: http://localhost:8000

## Тестирование

```bash
# Запустить все тесты
make test

# Тесты с coverage
make test-cov

# Linting
make lint

# Форматирование
make format
```

## Разработка

### Pre-commit hooks

```bash
pre-commit install
# Теперь при каждом git commit будут автоматически запускаться:
# - black (форматирование)
# - isort (сортировка импортов)
# - flake8 (linting)
# - mypy (проверка типов)
```

## Production Deployment

См. [DEPLOYMENT.md](DEPLOYMENT.md)
