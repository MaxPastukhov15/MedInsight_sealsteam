# Архитектура проекта

## Общая структура

```
Medical Analytics AI Agent
┌──────────────────────────────────────────────┐
│                 Frontend (React)                      │
│  - Chat UI                                         │
│  - Plotly Dashboard                                │
│  - Insights Cards                                  │
└─────────────────┬────────────────────────────┘
                  │ HTTP/REST API
                  ↓
┌──────────────────────────────────────────────┐
│              Backend (FastAPI)                     │
│  - REST API Endpoints                              │
│  - Request validation (Pydantic)                   │
│  - Structured logging                              │
│  - Rate limiting                                   │
└─────────────────┬────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │            │            │
      ↓            ↓            ↓
┌─────────┐  ┌─────────┐  ┌─────────┐
│ LangGraph│  │PostgreSQL│  │ChromaDB │
│  Agent   │  │ (on VPS) │  │  (RAG)  │
│  - State │  │  - Data  │  │-Insights│
│  - Tools │  │  - SQL   │  │-Vectors │
└─────────┘  └─────────┘  └─────────┘
      │
      ↓
┌──────────────────────────────────────────────┐
│          LLM ()                │
│  - Reasoning                                       │
│  - SQL generation                                  │
│  - Response formatting                             │
└──────────────────────────────────────────────┘
```

## Структура проекта

```
preparing/
├── backend/
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── chat.py            # POST /api/chat
│   │   └── visualize.py       # GET /api/trends, /api/geo
│   ├── agent/                  # LangGraph агент
│   │   ├── __init__.py
│   │   ├── graph.py           # LangGraph state + nodes
│   │   ├── tools.py           # SQL tools, forecast tools
│   │   └── prompts/
│   │       └── system.md      # System prompt
│   ├── database/               # База данных
│   │   ├── __init__.py
│   │   ├── connection.py      # SQLAlchemy подключение
│   │   └── models.py          # ORM модели
│   ├── rag/                    # RAG система
│   │   ├── __init__.py
│   │   ├── chromadb_client.py # ChromaDB клиент
│   │   └── retriever.py       # Поиск инсайтов
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── llm.py             # LLM service with retry
│   │   └── analytics.py       # Функции анализа
│   ├── schemas/                # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── chat.py            # ChatRequest, ChatResponse
│   │   └── analytics.py       # TrendsRequest, GeoRequest
│   ├── scripts/                # Утилиты
│   │   ├── load_data.py       # Загрузка CSV → PostgreSQL
│   │   └── generate_insights.py # Генерация insights.json
│   ├── config/                 # Конфигурация
│   │   ├── __init__.py
│   │   └── settings.py        # Pydantic Settings
│   ├── tests/                  # Тесты
│   │   ├── test_api.py
│   │   ├── test_agent.py
│   │   └── test_database.py
│   ├── .env.example           # Шаблон переменных
│   ├── requirements.txt       # Python зависимости
│   ├── requirements-ci.txt    # Dev tools
│   └── main.py                # Точка входа
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   └── Dashboard/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── data/                       # Данные (не коммитим)
│   ├── raw/                    # Исходные CSV
│   ├── insights.json           # Найденные инсайты
│   └── chroma/                 # ChromaDB хранилище
├── docs/
│   ├── ARCHITECTURE.md         # Этот файл
│   └── DATABASE_SETUP.md       # Инструкция по БД
├── docker-compose.yml          # Docker для локальной разработки
├── Makefile                    # Команды разработки
├── .gitignore
└── README.md
```

## Поток данных

### 1. Пользователь задаёт вопрос
```
Пользователь: "Покажи тренд по гриппу"
     ↓
Frontend (React)
     ↓ POST /api/chat
Backend (FastAPI)
     ↓
LangGraph Agent
```

### 2. Агент обрабатывает вопрос
```
LangGraph Agent:
  1. Node: RAG Retrieval
     ↓ Поиск инсайтов в ChromaDB
     ↓ "Найден: Пик простуд в октябре"
     
  2. Node: SQL Planner
     ↓ LLM генерирует SQL
     ↓ "SELECT date_trunc('month', date), COUNT(*) FROM disease_cases WHERE disease='грипп' GROUP BY 1"
     
  3. Node: SQL Executor
     ↓ Выполнение SQL в PostgreSQL
     ↓ [{"2024-01": 100}, {"2024-02": 120}, ...]
     
  4. Node: Responder
     ↓ LLM форматирует ответ
     ↓ "Тренд по гриппу: пик в октябре (120 случаев). Согласно инсайту #3..."
```

### 3. Ответ пользователю
```
Backend → Frontend
     ↓
Пользователь видит:
  - Текстовый ответ
  - График трендов (Plotly)
  - Источники ("Инсайт #3")
```

## Технологии

### Backend
- **FastAPI** - async REST API
- **SQLAlchemy** - ORM для PostgreSQL
- **LangChain** - LLM оркестрация
- **LangGraph** - agentic workflows
- **ChromaDB** - vector database для RAG
- **Pandas** - обработка данных
- **Prophet** - прогнозирование (опционально)
- **Structlog** - структурированное логирование

### Frontend
- **React** - UI фреймворк
- **Plotly.js** - интерактивные графики
- **Tailwind CSS** - стилизация

### Infrastructure
- **PostgreSQL** - на VPS (1GB RAM, 10GB storage)
- **Docker** - локальная разработка
- **Render/Railway** - backend deploy
- **Vercel** - frontend deploy

## API Endpoints

### Chat
```
POST /api/chat
Request:
{
  "message": "Покажи тренд по гриппу",
  "session_id": "user123"
}

Response:
{
  "response": "Тренд по гриппу: пик в октябре...",
  "sources": ["insight_3"],
  "confidence": 0.92,
  "visualization": {
    "type": "line_chart",
    "data": [...]
  }
}
```

### Visualization
```
GET /api/trends?disease=грипп&period=12m
Response:
{
  "data": [
    {"month": "2024-01", "cases": 100},
    {"month": "2024-02", "cases": 120}
  ]
}

GET /api/geo?disease=диабет
Response:
{
  "data": [
    {"district": "Центральный", "cases": 250},
    {"district": "Приморский", "cases": 180}
  ]
}
```

## Безопасность

### SQL Injection Protection
- Использовать SQLAlchemy ORM
- Параметризованные запросы
- Валидация SQL агента: только SELECT

### API Security
- CORS: только доверенные origins
- Rate limiting: 60 запросов/минуту
- Input validation: Pydantic схемы

### VPS Security
- Firewall: только 5432 порт для PostgreSQL
- Strong passwords
- SSL/TLS для production (опционально)

## Production Deploy

### Backend (Render/Railway)
```bash
# Environment variables:
DATABASE_URL=postgresql://med_user:pass@vps_ip:5432/medical_analytics
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=lsv2_...
```

### Frontend (Vercel)
```bash
# Environment variables:
VITE_API_URL=https://your-backend.render.com
```

## Monitoring

### Метрики (Prometheus)
- Request latency (p50, p95, p99)
- Error rate
- Database connection pool
- LLM API calls

### Логи (Structlog)
- Request/Response logging
- Agent decision traces
- SQL query logging
- Error tracking

### LangSmith
- Agent traces
- LLM calls
- Tool usage
- Debug playground
