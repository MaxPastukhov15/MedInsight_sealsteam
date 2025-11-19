# Архитектура системы

## Общая структура

```
Пользователь
    ↓
 React Frontend (TypeScript + Vite)
    ↓ HTTP/REST
 FastAPI Backend
    │
    ├── LangGraph Agent (AI Orchestration)
    │   ├── LLM Provider (Ollama/Together/OpenAI)
    │   └── 5 Tools (Scenarios)
    │
    ├── PostgreSQL (Data Storage)
    ├── Redis (Caching)
    └── ChromaDB (Vector Search - RAG)
```

## Компоненты

### Backend

#### FastAPI Application
- **Роль**: REST API server
- **Ответственность**: Обработка HTTP запросов, валидация, marshalling
- **Технологии**: FastAPI, Pydantic, Uvicorn

#### LangGraph Agent
- **Роль**: AI-orchestration layer
- **Ответственность**: Принятие решений, вызов инструментов, генерация ответов
- **Pattern**: ReAct (Reasoning + Acting)

#### 5 Аналитических Сценариев
1. **Disease Analysis** - Анализ текущей заболеваемости
2. **Trend Analysis** - Выявление трендов
3. **Forecasting** - Прогнозирование (Prophet + ARIMA)
4. **Recommendations** - Рекомендации (RAG + LLM)
5. **Pattern Detection** - Поиск паттернов

#### PostgreSQL
- **Роль**: Основное хранилище данных
- **Таблицы**: Disease, Forecast, AnalysisCache, ChatHistory
- **ORM**: SQLAlchemy (async)

#### Redis
- **Роль**: In-memory cache
- **Цель**: Ускорение ответов (<5 сек)
- **TTL**: 2-60 минут в зависимости от типа данных

#### ChromaDB
- **Роль**: Vector database для RAG
- **Данные**: Медицинские протоколы и рекомендации
- **Embeddings**: sentence-transformers

### Frontend

#### React Application
- **UI Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Структура**:
  - ChatInterface (левая панель)
  - VisualizationDashboard (правая панель)
  - MetricsPanel (нижняя панель)

#### Plotly
- **Роль**: Интерактивные графики
- **Типы**: Line charts, bar charts, scatter plots

## Поток данных

```
1. Пользователь отправляет сообщение
   ↓
2. FastAPI принимает POST /api/v1/chat
   ↓
3. Проверка Redis cache
   │
   ├─ Cache HIT → Возвращаем результат
   └─ Cache MISS → Продолжаем
       ↓
4. LangGraph Agent анализирует запрос
   ↓
5. Agent выбирает инструменты (Scenario 1-5)
   ↓
6. Инструменты запрашивают данные из PostgreSQL
   ↓
7. Выполняются вычисления (numpy, scipy, pandas)
   ↓
8. Генерируются визуализации (Plotly JSON)
   ↓
9. Agent генерирует текстовый ответ
   ↓
10. Результат сохраняется в Redis
   ↓
11. Возвращаем JSON в Frontend
```

## Масштабирование

- **Horizontal**: Несколько инстансов backend за load balancer
- **Caching**: Redis снижает нагрузку на БД
- **Database**: Connection pooling, индексы
- **Async**: SQLAlchemy async, Redis async
