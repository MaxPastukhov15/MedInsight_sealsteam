# Medical Analytics AI-Agent

> AI-агент для анализа медицинских данных с прогнозированием и рекомендациями

## Основные возможности

- 📊 **Анализ заболеваемости** - текущие показатели по регионам и возрастным группам
- 📈 **Анализ трендов** - выявление роста/снижения заболеваемости
- 🔮 **Прогнозирование** - Prophet + ARIMA ensemble на 14 дней
- 💡 **Рекомендации** - RAG-протоколы + LLM генерация
- 🔍 **Поиск паттернов** - аномалии, корреляции, сезонность

## Предварительные требования

- **Python 3.11+**
- **PostgreSQL 15+** (опционально, для persistence)
- **Redis 7+**       (опционально, для кэширования)
- **Node.js 18+**


## Quick Start

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Ronshin-Vsevolod/preparing.git
cd preparing
```

### 2. Установить зависимости

**Автоматически (рекомендуется):**

```bash
make setup
source .venv/bin/activate
```

Эта команда создаст `.venv`, установит все зависимости и настроит окружение.

**Вручную (альтернатива):**

```bash
# Создать venv
python3.11 -m venv .venv

# Активировать (Linux/macOS)
source .venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r backend/requirements-ci.txt
```

### 3. Запустить backend

## Основные команды

| Команда | Описание |
|---------|-------------|
| `make setup` | Создать `.venv` и установить зависимости из `backend/requirements.txt` |
| `make dev` | Запустить backend на `localhost:8000` (uvicorn с hot-reload) |
| `make freeze` | Обновить `backend/requirements.txt` из установленных пакетов |
| `make format` | Форматировать код с ruff |
| `make lint` | Проверка кода с ruff |
| `make check` | Проверка типов с mypy |
| `make test` | Запустить pytest тесты (заглушка, раскомментируйте когда тесты готовы) |
| `make clean` | Удалить `.venv` директорию |

Полный список: `make help`

## Управление зависимостями

### Добавить пакет

```bash
source .venv/bin/activate
pip install новый-пакет

# Обновить requirements.txt
pip freeze > backend/requirements.txt
```

### Просмотреть установленные пакеты

```bash
make freeze
```

## Структура проекта

```
preparing/
├── backend/              # FastAPI backend
│   ├── config/           # Конфигурация
│   ├── database/         # БД модели и подключение
│   ├── cache/            # Redis кэширование
│   ├── rag/              # RAG pipeline (ChromaDB + embeddings)
│   ├── agent/            # LangGraph AI-агент
│   ├── scenarios/        # 5 аналитических сценариев
│   ├── api/              # FastAPI routes
│   ├── monitoring/       # Логирование и метрики
│   ├── tests/            # Тесты
│   └── requirements.txt  # Зависимости проекта
├── frontend/             # React + TypeScript
├── docs/                 # Документация
├── .github/              # GitHub Actions CI/CD
├── .venv/                # Virtual environment (не в git)
├── README.md             # Этот файл
├── Makefile              # Команды разработки
└── .venv/                # Virtual environment (создаётся через make setup)
```

## Технологии

### Backend
- **FastAPI** - REST API framework
- **LangChain + LangGraph** - AI agent orchestration
- **SQLAlchemy** - ORM for PostgreSQL
- **ChromaDB** - Vector database for RAG
- **Redis** - Caching
- **Prophet + ARIMA** - Time series forecasting
- **Structlog** - Structured logging

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Plotly** - Interactive visualizations

### DevOps
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **pytest** - Testing framework
- **ruff, mypy,** - Code quality

## Документация

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Техническая архитектура
- [ALGORITHMS.md](docs/ALGORITHMS.md) - Математические алгоритмы
- [API_SPEC.md](docs/API_SPEC.md) - API спецификация

## CI/CD

Проект использует GitHub Actions для:
- ✅ Автоматического тестирования (pytest)
- ✅ Проверки качества кода (mypy, ruff)
- ✅ Code coverage анализ
- ✅ Автоматического deployment

## License

MIT
