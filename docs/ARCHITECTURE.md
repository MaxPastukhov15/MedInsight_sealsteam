# Medical Analytics Agent - Architecture

## Overview

LangGraph-based medical analytics agent with parallel tool calling support.

## Key Features

- **Parallel Tool Calls**: Model can call multiple tools in one response (requires compatible model)
- **State Persistence**: Codes and SQL are tracked across steps for reuse
- **Forecast Integration**: Forecast data can be included in charts
- **SSE Streaming**: Real-time updates to frontend

## Supported Models

| Model | Parallel Tools | Size | Recommended |
|-------|---------------|------|-------------|
| `qwen/qwen3-32b` | ✅ 3 tools | 32B | ✅ Yes |
| `openai/gpt-4o-mini` | ✅ 3 tools | - | ✅ Yes (paid) |
| `qwen/qwen3-coder-30b-a3b-instruct` | ❌ 1 tool | 30B | No |
| `meta-llama/llama-3.3-70b-instruct` | ❌ 1 tool | 70B | No |

**Note**: Models without parallel tool support will work but require more LLM calls (slower).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                    (React + Plotly)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ SSE Stream
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     api.py (FastAPI)                         │
│  POST /chat/stream  │  POST /chat/history  │  GET /health   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    graph.py (LangGraph)                      │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐                 │
│  │  agent  │───▶│  tools  │───▶│ finalize │                 │
│  └─────────┘    └─────────┘    └──────────┘                 │
│       │              │                                       │
│       │   ┌──────────┴──────────┐                           │
│       │   │   State Tracking    │                           │
│       │   │  - found_codes      │                           │
│       │   │  - last_sql         │                           │
│       │   │  - visualization    │                           │
│       │   └─────────────────────┘                           │
└───────┼─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                     tools.py                                 │
│  ┌──────────────┐  ┌─────────┐  ┌────────────────┐          │
│  │ search_codes │  │ run_sql │  │ forecast_trend │          │
│  └──────────────┘  └─────────┘  └────────────────┘          │
│  ┌──────────────┐                                           │
│  │ create_chart │                                           │
│  └──────────────┘                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   database.py (DuckDB)                       │
│  patients │ prescriptions │ diagnoses │ drugs               │
└─────────────────────────────────────────────────────────────┘
```

## Execution Flow

### With Parallel Tool Calls (qwen3-32b, gpt-4o-mini)

```
User: "тренд диабета по месяцам с прогнозом"
        │
        ▼
   LLM Call #1
        │
        ▼
   search_codes("диабет")
        │
        ▼
   LLM Call #2 (sees codes)
        │
        ├──▶ run_sql(...)
        ├──▶ forecast_trend(...)
        └──▶ create_chart(...)
        │
        ▼
   LLM Call #3
        │
        ▼
   Final Answer + Chart

Total: 3 LLM calls, ~15-25 seconds
```

### Without Parallel Tool Calls (other models)

```
User: "тренд диабета по месяцам с прогнозом"
        │
        ▼
   LLM Call #1 → search_codes
   LLM Call #2 → run_sql
   LLM Call #3 → forecast_trend
   LLM Call #4 → create_chart
   LLM Call #5 → Final Answer

Total: 5 LLM calls, ~40-60 seconds
```

## State Management

### MedicalAgentState

```python
class MedicalAgentState(AgentState):
    visualization_json: Optional[Dict]  # Plotly chart JSON
    final_response: Optional[Dict]      # Final answer
    step_count: int                     # Current step
    found_codes: List[str]              # Accumulated diagnosis/drug codes
    last_sql: Optional[str]             # Last successful SQL for reuse
```

### Special Features

#### {CODES} Placeholder
SQL can use `{CODES}` which gets replaced with found codes:
```sql
SELECT * FROM prescriptions WHERE diagnosis_code IN ({CODES})
-- Becomes:
SELECT * FROM prescriptions WHERE diagnosis_code IN ('E10', 'E11', 'E14')
```

#### REUSE_SQL
Tools can specify `sql="REUSE_SQL"` to reuse the last successful SQL:
```python
create_chart(sql="REUSE_SQL", chart_type="bar", ...)
```

#### include_forecast
Charts can include forecast data from previous `forecast_trend` call:
```python
create_chart(..., include_forecast=True)
```

## Configuration

### Environment Variables (.env)

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-xxx

# Model selection
MODEL_NAME=qwen/qwen3-32b

# Agent limits
MAX_STEPS=15
MAX_RETRIES=3
```

## Files

| File | Purpose |
|------|---------|
| `backend/graph.py` | LangGraph agent, system prompt, orchestration |
| `backend/tools.py` | Tool definitions (search_codes, run_sql, forecast_trend, create_chart) |
| `backend/api.py` | FastAPI endpoints, SSE streaming |
| `backend/state.py` | Agent state definition |
| `backend/database.py` | DuckDB connection and FTS indexing |
| `backend/config.py` | Logging configuration |

## Adding New Tools

See [TOOLS.md](./TOOLS.md) for detailed guide on creating new tools.

## Troubleshooting

### Model doesn't call multiple tools
- Check if model supports parallel tool calls (see table above)
- Verify `parallel_tool_calls=True` in `bind_tools()`

### Charts not created
- System prompt must emphasize chart creation
- Check if `create_chart` is in the tool calls

### Slow responses
- Use a model with parallel tool support
- Check OpenRouter rate limits

### SQL errors
- Verify column names match schema
- Use `DATE_TRUNC('month', ...)` for time grouping
- Use `DATE_DIFF('year', birth_date, CURRENT_DATE)` for age
