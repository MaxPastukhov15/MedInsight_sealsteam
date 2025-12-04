# Tools Documentation

## Current Tools

### 1. search_codes
Search for ICD diagnosis codes or drug codes.

```python
search_codes(table: "diagnoses" | "drugs", keywords: str) -> str
```

**Parameters:**
- `table`: Either `"diagnoses"` for ICD codes or `"drugs"` for medications
- `keywords`: Search terms separated by comma, e.g. `"диабет, E10, E11"`

**Returns:** Table of matching codes with scores

**Example:**
```
search_codes(table="diagnoses", keywords="диабет, сахарный")

# Output:
diagnosis_code  diagnosis_name                    score
E11             Сахарный диабет 2 типа           3.18
E10             Сахарный диабет 1 типа           3.18
E14             Сахарный диабет неуточненный     3.18
```

---

### 2. run_sql
Execute a DuckDB SQL query on the medical database.

```python
run_sql(sql: str) -> str
```

**Database Schema:**
- `patients`: patient_id, birth_date (DATE), gender, district, region
- `prescriptions`: patient_id, diagnosis_code, drug_code, prescription_date
- `diagnoses`: diagnosis_code, diagnosis_name
- `drugs`: drug_code, trade_name, full_name, price

**Special:**
- Use `{CODES}` placeholder - replaced with codes from `search_codes`
- Use `DATE_DIFF('year', birth_date, CURRENT_DATE)` for age calculation
- Use `DATE_TRUNC('month', prescription_date)` for monthly grouping

**Example:**
```sql
SELECT DATE_TRUNC('month', prescription_date) AS month, COUNT(*) AS cnt
FROM prescriptions 
WHERE diagnosis_code IN ({CODES})
GROUP BY month ORDER BY month
```

---

### 3. forecast_trend
Forecast future values using linear regression. **Run BEFORE create_chart** to include forecast in visualization.

```python
forecast_trend(sql: str, date_col: str, value_col: str, periods: int = 3) -> str
```

**Parameters:**
- `sql`: SQL query returning date and value columns
- `date_col`: Name of the date/period column
- `value_col`: Name of the value column to forecast
- `periods`: Number of future periods to predict (default 3)

**Returns:** Forecast values and trend direction

**Example:**
```
forecast_trend(
    sql="SELECT DATE_TRUNC('month', prescription_date) AS month, COUNT(*) AS cnt FROM prescriptions GROUP BY month",
    date_col="month",
    value_col="cnt",
    periods=3
)

# Output:
Прогноз (рост, 5.23/период):
2025-03: 2150.0
2025-04: 2155.2
2025-05: 2160.5
```

---

### 4. create_chart
Create a Plotly chart from SQL query results.

```python
create_chart(
    sql: str,
    chart_type: "bar" | "line" | "scatter" | "histogram" | "pie",
    x_col: str,
    y_col: str = None,
    title: str = "Chart",
    include_forecast: bool = False
) -> str
```

**Parameters:**
- `sql`: SQL query to get data (or `"REUSE_SQL"` to use previous SQL)
- `chart_type`: Type of chart
- `x_col`: Column name for X axis
- `y_col`: Column name for Y axis (optional for histogram/pie)
- `title`: Chart title
- `include_forecast`: If True, includes forecast data from previous `forecast_trend` call

**Example:**
```python
create_chart(
    sql="REUSE_SQL",
    chart_type="line",
    x_col="month",
    y_col="cnt",
    title="Тренд заболеваемости",
    include_forecast=True
)
```

---

## Tool Execution Flow

### Typical Analysis with Forecast

```
1. search_codes(table="diagnoses", keywords="диабет")
   → Returns: E10, E11, E14 codes
   → Stored in state.found_codes

2. run_sql(sql="SELECT ... WHERE diagnosis_code IN ({CODES}) ...")
   → {CODES} replaced with 'E10', 'E11', 'E14'
   → Stored in state.last_sql

3. forecast_trend(sql="REUSE_SQL", date_col="month", value_col="cnt")
   → Uses state.last_sql
   → Stores forecast in _last_forecast

4. create_chart(sql="REUSE_SQL", ..., include_forecast=True)
   → Uses state.last_sql
   → Includes _last_forecast data
   → Returns Plotly JSON
```

### Simple Analysis (no forecast)

```
1. run_sql(sql="SELECT district, COUNT(*) ...")
   → Stored in state.last_sql

2. create_chart(sql="REUSE_SQL", chart_type="bar", ...)
   → Uses state.last_sql
   → Returns Plotly JSON
```

---

## Adding New Tools

### Step 1: Create the tool in tools.py

```python
from langchain_core.tools import tool

@tool
def my_new_tool(param1: str, param2: int = 10) -> str:
    """
    Description for LLM - this is what the model sees to decide when to use the tool.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default 10)
    """
    # Your logic here
    result = do_something(param1, param2)
    return f"Result: {result}"
```

### Step 2: Add to TOOLS list

```python
# At the end of tools.py
TOOLS = [search_codes, run_sql, forecast_trend, create_chart, my_new_tool]
```

### Step 3: Update system prompt (if needed)

If the tool should be called in specific situations, update `SYSTEM_PROMPT` in `graph.py`.

---

## Global State in tools.py

```python
_db = Database("data")      # Database connection
_last_chart = None          # Last created chart (Plotly JSON)
_last_forecast = None       # Last forecast data (DataFrame)
```

### get_last_chart()

Helper function to retrieve and clear the last chart:

```python
def get_last_chart():
    """Get and clear the last chart."""
    global _last_chart
    chart = _last_chart
    _last_chart = None
    return chart
```

Used by `graph.py` to capture chart after `create_chart` execution.

---

## Best Practices

1. **Clear descriptions** - LLM decides which tool to use based on docstring
2. **Return strings** - Tools should return human-readable strings
3. **Handle errors** - Always return error messages, don't raise exceptions
4. **Preview data** - Don't return huge datasets, use `.head(20)`
5. **Use REUSE_SQL** - Avoid duplicate SQL execution
