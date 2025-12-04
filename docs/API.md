# Medical Insight API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Chat Stream (SSE)
**POST** `/chat/stream`

Отправляет запрос и получает ответ в виде Server-Sent Events (SSE).

**Request:**
```json
{
  "query": "Сколько пациентов с диабетом?",
  "thread_id": "session_xxx" // опционально, для продолжения диалога
}
```

**Response:** Stream событий в формате SSE

#### События:

**`step`** — Агент вызывает инструмент или думает
```json
{
  "type": "step",
  "step": 1,
  "tool": "search_codes",  // или "execute_sql", "generate_visualization", "thought"
  "thought": "текст мысли",  // только если tool="thought"
  "duration": 0.52
}
```

**`tool_result`** — Результат выполнения инструмента
```json
{
  "type": "tool_result",
  "result": "Rows: 10. Cols: ['name', 'count']...",  // превью до 300 символов
  "duration": 0.03
}
```

**`visualization`** — Сгенерирован график
```json
{
  "type": "visualization",
  "data": { /* Plotly JSON */ }
}
```

**`final`** — Финальный ответ
```json
{
  "type": "final",
  "answer": "Всего 7257 пациентов с диабетом.",
  "insights": ["7257 patients have diabetes"],
  "visualization": { /* Plotly JSON или null */ },
  "thread_id": "session_xxx"
}
```

**`error`** — Ошибка
```json
{
  "type": "error",
  "message": "Rate limit exceeded"
}
```

### 2. История чата
**POST** `/chat/history`

**Request:**
```json
{
  "thread_id": "session_xxx"
}
```

**Response:**
```json
{
  "messages": [
    {"role": "human", "content": "Сколько пациентов?"},
    {"role": "ai", "content": "Всего 379076 пациентов."}
  ],
  "thread_id": "session_xxx"
}
```

### 3. Удаление чата
**DELETE** `/chat/history/{thread_id}`

**Response:**
```json
{
  "status": "deleted",
  "thread_id": "session_xxx"
}
```

### 4. Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "ok",
  "checkpointer": "memory"
}
```

---

## Пример использования (JavaScript)

```javascript
async function sendMessage(query, threadId = null) {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, thread_id: threadId })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      
      const data = JSON.parse(line.substring(6));
      
      switch (data.type) {
        case 'step':
          console.log(`Step ${data.step}: ${data.tool}`);
          break;
        case 'tool_result':
          console.log('Result:', data.result);
          break;
        case 'visualization':
          // Отрисовать график с Plotly
          Plotly.newPlot('chart', data.data.data, data.data.layout);
          break;
        case 'final':
          console.log('Answer:', data.answer);
          // Сохранить thread_id для следующих запросов
          break;
        case 'error':
          console.error('Error:', data.message);
          break;
      }
    }
  }
}
```
