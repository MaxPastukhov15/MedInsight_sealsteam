# Medical Analytics AI-Agent

> AI-агент для анализа медицинских данных с прогнозированием и рекомендациями

## Основные возможности

- 📊 **Анализ заболеваемости** - текущие показатели по регионам и возрастным группам
- 📈 **Анализ трендов** - выявление роста/снижения заболеваемости
- 🔮 **Прогнозирование** - Prophet + ARIMA ensemble на 14 дней
- 💡 **Рекомендации** - RAG-протоколы + LLM генерация
- 🔍 **Поиск паттернов** - аномалии, корреляции, сезонность

## Quick Start

### Предварительные требования

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (для фронтенда)

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/Ronshin-Vsevolod/preparing.git
cd preparing

# Установить backend зависимости
make install-dev

# Скопировать .env.example
cp backend/.env.example backend/.env
# Отредактируйте backend/.env с вашими настройками

# Запустить БД и Redis через Docker
docker-compose up -d postgres redis

# Запустить backend
make run
```

### Тестирование

```bash
# Запустить все тесты
make test

# Запустить тесты с coverage
make test-cov

# Запустить linting
make lint

# Форматировать код
make format
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
│   └── tests/            # Тесты
├── frontend/             # React + TypeScript frontend
├── docs/                 # Документация
├── .github/              # GitHub Actions CI/CD
└── infra/                # Docker, docker-compose
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
- **black, isort, mypy, flake8** - Code quality

## Документация

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Техническая архитектура
- [ALGORITHMS.md](docs/ALGORITHMS.md) - Математические алгоритмы
- [SETUP.md](docs/SETUP.md) - Установка и запуск
- [API_SPEC.md](docs/API_SPEC.md) - API спецификация

## CI/CD

Проект использует GitHub Actions для:
- ✅ Автоматического тестирования (pytest)
- ✅ Проверки качества кода (mypy, black, isort, flake8)
- ✅ Code coverage анализ
- ✅ Автоматического deployment

## License

MIT
