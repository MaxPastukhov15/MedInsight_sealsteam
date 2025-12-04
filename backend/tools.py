"""Medical analytics tools for the agent."""
import json
from typing import Literal, Optional

import pandas as pd
import numpy as np
import plotly.express as px

from langchain_core.tools import tool
from backend.database import Database

# Global state
_db = Database("data")
_last_chart = None
_last_forecast = None


def get_last_chart():
    """Get and clear the last chart."""
    global _last_chart
    chart = _last_chart
    _last_chart = None
    return chart


@tool
def search_codes(table: Literal["diagnoses", "drugs"], keywords: str) -> str:
    """Search for ICD diagnosis codes or drug codes.
    
    Args:
        table: Either 'diagnoses' for ICD codes or 'drugs' for medications
        keywords: Search terms separated by comma, e.g. "диабет, E10, E11"
    """
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.replace('"', '').split(',') if k.strip()]
    
    col_id = "diagnosis_code" if table == "diagnoses" else "drug_code"
    col_text = "diagnosis_name" if table == "diagnoses" else "full_name"
    
    # FTS search
    search_q = " ".join(keywords).replace("'", "")
    sql = f"""
        SELECT {col_id}, {col_text}, fts_main_{table}.match_bm25({col_id}, ?) AS score
        FROM {table} WHERE score IS NOT NULL ORDER BY score DESC LIMIT 15
    """
    df, err = _db.execute(sql, [search_q])
    
    # Fallback to ILIKE
    if err or df is None or df.empty:
        conds = " OR ".join([f"{col_text} ILIKE '%{k}%'" for k in keywords])
        df, err = _db.execute(f"SELECT {col_id}, {col_text} FROM {table} WHERE {conds} LIMIT 15")
    
    if err:
        return f"Error: {err}"
    if df is None or df.empty:
        return "No matches found"
    return df.to_string(index=False)


@tool  
def run_sql(sql: str) -> str:
    """Execute a DuckDB SQL query on the medical database.
    
    Schema:
    - patients: patient_id, birth_date (DATE), gender, district, region
    - prescriptions: patient_id, diagnosis_code, drug_code, prescription_date
    - diagnoses: diagnosis_code, diagnosis_name
    - drugs: drug_code, full_name, price
    
    Use DATE_DIFF('year', birth_date, CURRENT_DATE) for age calculation.
    """
    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "Query returned no results"
    return f"Rows: {len(df)}, Columns: {list(df.columns)}\n{df.head(20).to_string(index=False)}"


@tool
def forecast_trend(sql: str, date_col: str, value_col: str, periods: int = 3) -> str:
    """Forecast future values using linear regression. Run BEFORE create_chart.
    
    Args:
        sql: SQL query returning date and value columns
        date_col: Name of the date/period column
        value_col: Name of the value column to forecast
        periods: Number of future periods to predict (default 3)
    """
    global _last_forecast
    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "No data for forecast"
    
    try:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        y = df[value_col].values.astype(float)
        
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        
        future_x = np.arange(len(y), len(y) + periods)
        future_y = slope * future_x + intercept
        
        last_date = df[date_col].iloc[-1]
        freq = pd.infer_freq(df[date_col]) or 'MS'
        future_dates = pd.date_range(last_date, periods=periods + 1, freq=freq)[1:]
        
        _last_forecast = pd.DataFrame({date_col: future_dates, value_col: future_y})
        
        results = [f"{d.strftime('%Y-%m')}: {v:.1f}" for d, v in zip(future_dates, future_y)]
        trend = "рост" if slope > 0 else "снижение"
        return f"Прогноз ({trend}, {slope:.2f}/период):\n" + "\n".join(results)
    except Exception as e:
        return f"Forecast error: {e}"


@tool
def create_chart(sql: str, chart_type: Literal["bar", "line", "scatter", "histogram", "pie"], 
                 x_col: str, y_col: Optional[str] = None, title: str = "Chart",
                 include_forecast: bool = False) -> str:
    """Create a Plotly chart from SQL query results.
    
    Args:
        sql: SQL query to get data
        chart_type: Type of chart (bar, line, scatter, histogram, pie)
        x_col: Column name for X axis
        y_col: Column name for Y axis (optional for histogram/pie)
        title: Chart title
        include_forecast: Include forecast data from previous forecast_trend call
    """
    global _last_chart, _last_forecast
    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "No data for chart"
    
    try:
        # Include forecast if available
        if include_forecast and _last_forecast is not None and y_col:
            df = df.copy()
            df["_type"] = "actual"
            forecast_df = _last_forecast.copy()
            forecast_df["_type"] = "forecast"
            forecast_df = forecast_df.rename(columns={
                forecast_df.columns[0]: x_col,
                forecast_df.columns[1]: y_col
            })
            df = pd.concat([df, forecast_df[[x_col, y_col, "_type"]]], ignore_index=True)
        
        # Create chart
        color = "_type" if "_type" in df.columns else None
        if chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, color=color, title=title)
        elif chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color=color, title=title)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=title)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, title=title)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=title)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
        
        _last_chart = json.loads(fig.to_json())
        return f"Chart created: {title}"
    except Exception as e:
        return f"Chart error: {e}"


TOOLS = [search_codes, run_sql, forecast_trend, create_chart]
