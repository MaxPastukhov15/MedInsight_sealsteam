# API Спецификация

## Base URL

```
Development: http://localhost:8000
Production: https://your-api.railway.app
```

## Аутентификация

Пока не требуется (MVP)

## Endpoints

### GET /

Корневой endpoint с информацией о API

**Response:**
```json
{
  "message": "Medical Analytics AI-Agent API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs"
}
```

---

### GET /health

Проверка здоровья сервиса

**Response:**
```json
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok",
  "llm": "ok",
  "timestamp": "2025-11-19T14:30:00Z"
}
```

---

### POST /api/v1/chat

Диалоговый интерфейс с AI-агентом

**Request:**
```json
{
  "message": "Какой грипп в СПб сейчас?",
  "chat_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "response": "В Санкт-Петербурге наблюдается рост заболеваемости гриппом. За последние 7 дней зарегистрировано 1500 случаев (+12% по сравнению с предыдущей неделей).",
  "visualizations": [
    {
      "type": "line",
      "data": {...},
      "layout": {...}
    }
  ],
  "metrics": {
    "latency_ms": 1234,
    "cache_hit": false,
    "model": "ollama:mistral"
  },
  "tools_used": ["analyze_disease", "get_trends"]
}
```

---

### POST /api/v1/analyze

Анализ заболеваемости

**Request:**
```json
{
  "disease_name": "грипп",
  "region": "Санкт-Петербург",
  "age_group": "18-65",
  "days": 7
}
```

**Response:**
```json
{
  "disease_name": "грипп",
  "current_cases": 1500,
  "deaths": 5,
  "mortality_rate": 0.33,
  "status": "RISING",
  "trend_percentage": 12.5
}
```

---

### POST /api/v1/forecast

Прогнозирование заболеваемости

**Request:**
```json
{
  "disease_name": "грипп",
  "region": "Санкт-Петербург",
  "forecast_days": 14
}
```

**Response:**
```json
{
  "predictions": [150, 155, 160, 165, ...],
  "confidence_lower": [140, 145, 150, ...],
  "confidence_upper": [165, 170, 175, ...],
  "dates": ["2025-11-20", "2025-11-21", ...],
  "model": "ensemble_prophet_arima"
}
```

---

### GET /api/v1/metrics

Метрики производительности

**Response:**
```json
{
  "avg_latency_ms": 1200,
  "cache_hit_rate": 0.75,
  "total_requests": 1000,
  "errors": 5
}
```

---

## Коды ошибок

- `200` - Success
- `400` - Bad Request (неверные параметры)
- `404` - Not Found
- `422` - Validation Error (Pydantic)
- `500` - Internal Server Error
