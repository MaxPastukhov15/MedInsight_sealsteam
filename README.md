# Medical Analytics AI Agent

🏥 **AI-агент для анализа медицинских данных**

FastAPI + LangChain агент, который отвечает на вопросы о медицинских данных через SQL.

## ✨ Возможности

- 📈 **Анализ трендов** - сезонность заболеваний
- 🗺️ **География** - распределение по районам
- 🤖 **LLM агент** - генерирует SQL и отвечает на вопросы
- 💡 **Простая архитектура** - работает сразу

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонировать
git clone https://github.com/Ronshin-Vsevolod/preparing.git
cd preparing

# Установить зависимости
make install-dev

# Настроить .env
cp .env.example .env
nano .env  # Добавить DATABASE_URL и OPENAI_API_KEY
```

### 2. База данных

```bash
# Создать PostgreSQL базу
createbuser medical_analytics
createdb -O medical_analytics medical_analytics

# Загрузить данные
mkdir -p data/raw
# Положите CSV файлы в data/raw/

source .venv/bin/activate
python backend/scripts/load_data.py
```

### 3. Запуск

```bash
make run
# Перейти на http://localhost:8000/docs
```

## 📚 Структура

```
backend/
├── core/
│   └── config.py          # Настройки
├── database/
│   ├── connection.py      # SQLAlchemy
│   └── models.py          # DiseaseCase модель
├── api/
│   ├── chat.py            # POST /api/chat
│   └── visualize.py       # GET /api/trends, /api/geo
├── agent/
│   └── simple_agent.py    # LLM агент
├── scripts/
│   └── load_data.py       # Загрузка CSV
└── main.py                # FastAPI app
```

## 📡 API

### Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Сколько случаев гриппа?", "session_id": "test"}'
```

### Trends
```bash
curl "http://localhost:8000/api/trends?disease=грипп"
```

### Geography
```bash
curl "http://localhost:8000/api/geo?disease=диабет"
```

## 🛠️ Tech Stack

- **FastAPI** - async REST API
- **SQLAlchemy** - PostgreSQL ORM
- **LangChain** - LLM orchestration
- **OpenAI** - GPT-4o-mini
- **Pandas** - data processing

## 👥 Команда

- **Ваня** - Frontend
- **Макс** - Backend
- **Сева** - Database + ML
- **Вася** - LLM Agent
- **Лёша** - Data Science

---

**Сделано для хакатона** ❤️
