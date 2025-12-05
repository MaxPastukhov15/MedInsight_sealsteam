import json
from typing import Literal, Optional

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from langchain_core.tools import tool
from backend.database import Database


# Global state
_db = Database("data/processed")
_last_chart = None
_last_forecast = None


def get_last_chart():
    """Get and clear the last chart."""
    global _last_chart
    chart = _last_chart
    _last_chart = None
    return chart


@tool
def search_codes(table: Literal["diagnoses", "drugs"], keywords: list[str] | str) -> str:
    """Search for ICD diagnosis codes or drug codes.

    Args:
        table: Either 'diagnoses' for ICD codes or 'drugs' for medications
        keywords: Search terms separated by comma, e.g. "диабет, E10, E11"
    """
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.replace('"', "").split(",") if k.strip()]

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
    - patients: patient_id, birth_dt, age, gender, district, region
    - prescriptions: prescription_id, patient_id, diagnosis_code, drug_id, date, year, month
    - diagnoses: diagnosis_code, diagnosis_name, disease_class
    - medications: drug_id, trade_name, full_name, dosage, price
    """
    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "Query returned no results"
    return f"Rows: {len(df)}, Columns: {list(df.columns)}\n{df.head(20).to_string(index=False)}"


@tool
def forecast_trend(
    sql: str,
    days: int = 30,
    max_history_days: Optional[int] = None,
    auto_aggregate: bool = True,
) -> str:
    """Forecast disease incidence using Prophet+SARIMA ensemble.

    Args:
        sql: SQL query returning 'date' (DATE) and 'cases' (INT) columns
        days: Forecast horizon in days (14-365)
        max_history_days: Limit historical data to last N days (None=use all)
        auto_aggregate: Automatically aggregate sparse data (default True)
    """
    global _last_forecast
    from backend.forecast_trend import generate_forecast, ForecastError

    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "No data for forecast"

    # Drop rows with null dates
    df = df.dropna(subset=["date"])

    try:
        result = generate_forecast(
            df=df,
            days=days,
            max_history_days=max_history_days,
            use_ensemble=True,
            auto_aggregate=auto_aggregate,
        )

        _last_forecast = pd.DataFrame(result["forecast"])
        _last_forecast["date"] = pd.to_datetime(_last_forecast["date"])

        warnings_text = ""
        if result["data_quality"]["warnings"]:
            warnings_text = "\nWarnings: " + "; ".join(result["data_quality"]["warnings"][:3])

        msg = (
            f"Model: {result['model_used']} | Confidence: {result['model_confidence']} | "
            f"Aggregation: {result['data_quality']['aggregation']}{warnings_text}\n\n"
        )
        for item in result["forecast"][:7]:
            msg += f"{item['date']}: {item['predicted']} (CI: {item['lower_bound']}-{item['upper_bound']})\n"
        if len(result["forecast"]) > 7:
            msg += f"... ({len(result['forecast']) - 7} more points)"

        return msg
    except ForecastError as e:
        return f"Forecast Error: {e}"
    except Exception as e:
        return f"Forecast error: {e}"


@tool
def create_visualization(code: str) -> str:
    """Execute Python code to create a Plotly visualization.

    IMPORTANT: There is NO pre-existing 'df' variable! You MUST fetch data first using db.execute().

    Available variables:
    - db: Database instance with db.execute(sql) -> (df, err)
    - pd, px, go, np: pandas, plotly.express, plotly.graph_objects, numpy
    - forecast_df: DataFrame from last forecast_trend call (columns: date, predicted, lower_bound, upper_bound)
    - datetime, timedelta, json

    REQUIRED: Assign final figure to variable `fig`.

    CORRECT example:
        df, err = db.execute("SELECT district, COUNT(*) as cnt FROM patients GROUP BY district")
        fig = px.bar(df, x='district', y='cnt', title='Patients by District')

    WRONG (will fail with 'df is not defined'):
        fig = px.bar(df, x='district', y='cnt')  # ERROR: df does not exist!
    """
    global _last_chart, _last_forecast

    local_vars = {
        "db": _db,
        "pd": pd,
        "px": px,
        "go": go,
        "np": np,
        "forecast_df": _last_forecast,
        "datetime": datetime,
        "timedelta": timedelta,
        "json": json,
    }

    safe_builtins = {
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "reversed": reversed,
        "filter": filter,
        "map": map,
        "any": any,
        "all": all,
        "isinstance": isinstance,
        "type": type,
        "print": print,
        "None": None,
        "True": True,
        "False": False,
    }

    try:
        exec(code, {"__builtins__": safe_builtins}, local_vars)
        fig = local_vars.get("fig")
        if fig is None:
            return "Error: code must assign figure to 'fig' variable"
        _last_chart = json.loads(fig.to_json())
        return "Chart created successfully"
    except Exception as e:
        return f"Error: {e}"


TOOLS = [search_codes, run_sql, forecast_trend, create_visualization]
