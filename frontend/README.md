# Frontend - Medical Analytics Dashboard

> React + TypeScript + Vite frontend для Medical Analytics AI-Agent

## TODO: Реализовать

### Структура:

```
frontend/
├── package.json              # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── .env.example             # Environment template
└── src/
    ├── main.tsx             # Entry point
    ├── App.tsx              # Main component
    ├── components/
    │   ├── ChatInterface.tsx
    │   ├── VisualizationDashboard.tsx
    │   ├── MetricsPanel.tsx
    │   └── LoadingSpinner.tsx
    ├── hooks/
    │   ├── useChat.ts
    │   └── useVisualization.ts
    ├── services/
    │   └── api.ts           # API client
    ├── types/
    │   └── index.ts         # TypeScript types
    └── styles/
        └── globals.css      # Global styles
```

### Технологии:
- React 18
- TypeScript
- Vite
- Plotly.js (визуализации)
- Axios/Fetch (запросы к API)

### Компоненты:

**ChatInterface** - левая панель
- Чат с AI-агентом
- История сообщений
- Input для запросов

**VisualizationDashboard** - правая панель
- Plotly графики
- Line charts, bar charts, scatter plots
- Интерактивность

**MetricsPanel** - нижняя панель
- Latency
- Cache hit rate
- Active queries

---

## Запуск (когда реализован):

```bash
cd frontend
npm install
npm run dev
```

Откроется на: http://kakoitohost:****
