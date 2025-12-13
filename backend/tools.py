import json
from typing import Literal, Optional

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from langchain_core.tools import tool
from backend.database import Database
from backend.disease_classifier import DiseaseClassifier


# Global state
_db = Database("data/processed")
_classifier = DiseaseClassifier("disease_definitions.json")
_last_chart = None
_last_forecast = None
_last_anomaly_data = None


def get_last_chart():
    """Get and clear the last chart."""
    global _last_chart
    chart = _last_chart
    _last_chart = None
    return chart


def get_last_forecast_data():
    """Get and clear the last forecast data."""
    global _last_forecast
    data = _last_forecast
    _last_forecast = None
    return data


def get_last_anomaly_data():
    """Get and clear the last anomaly detection data."""
    global _last_anomaly_data
    data = _last_anomaly_data
    _last_anomaly_data = None
    return data


@tool
def search_codes(table: Literal["diagnoses", "drugs"], keywords: list[str] | str) -> str:
    """Search for ICD diagnosis codes or drug codes.

    Args:
        table: Either 'diagnoses' for ICD codes or 'drugs' for medications
        keywords: Search terms separated by comma, e.g. "диабет, E10, E11"
    """
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.replace('"', "").split(",") if k.strip()]

    results = []

    if table == "diagnoses":
        kb_hits = []
        for k in keywords:
            groups = _classifier.search_groups(k)
            for g_name, g_desc in groups:
                kb_hits.append(f"GROUP: '{g_name}' ({g_desc}) -> Use analyze_health_trends('{g_name}')")

        if kb_hits:
            results.append("--- KNOWLEDGE BASE MATCHES ---")
            results.extend(list(set(kb_hits)))
            results.append("\n")

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

    if not (df is None or df.empty):
        results.append("--- DATABASE INDIVIDUAL CODES ---")
        results.append(df.to_string(index=False))
    if not results:
        return "No matches found"
    return "\n".join(results)


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
    global _last_chart, _last_forecast, _last_anomaly_data

    local_vars = {
        "db": _db,
        "pd": pd,
        "px": px,
        "go": go,
        "np": np,
        "forecast_df": _last_forecast,
        "anomaly_data": _last_anomaly_data,
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


@tool
def detect_outbreak(
    sql: str,
    threshold_sigma: float = 2.5,
) -> str:
    """
    Detect temporal disease outbreaks (spikes/drops over time).

    IMPORTANT: SQL MUST return exactly these column aliases:
    1. 'date' (DATE)
    2. 'cases' (INT)

    Example:
    SELECT date, COUNT(*) as cases FROM prescriptions ... GROUP BY date

    threshold_sigma: 2.0=loose, 2.5=moderate (default), 3.0=strict
    """
    global _last_anomaly_data

    from backend.anomaly_detection import detect_timeseries_anomalies
    from backend.forecast_trend import ForecastError

    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "No data for outbreak detection"

    df = df.dropna(subset=["date"])

    try:
        result = detect_timeseries_anomalies(
            df=df,
            threshold_sigma=threshold_sigma,
        )

        _last_anomaly_data = result

        if result["total"] == 0:
            return (
                f"No outbreaks detected in period {result['period']} "
                f"({result['data_points']} points, threshold {threshold_sigma}σ)"
            )

        lines = [f"Found {result['total']} outbreak(s) in period {result['period']}:\n"]

        for a in result["anomalies"][:10]:
            sign = "+" if a["direction"] == "spike" else "-"
            lines.append(
                f"  • {a['date']}: {a['actual']} cases "
                f"(expected {a['expected']}, {sign}{abs(a['deviation'])}, "
                f"z={a['z_score']})"
            )

        if result["total"] > 10:
            lines.append(f"\n... and {result['total'] - 10} more anomalies")

        if result.get("warnings"):
            lines.append("\n⚠️ " + result["warnings"][0])

        return "\n".join(lines)

    except ForecastError as e:
        return f"Outbreak Detection Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


@tool
def detect_geographic_outliers(
    sql: str,
    sensitivity: float = 1.5,
) -> str:
    """
    Detect outlier districts/age groups/categories using IQR method.

    IMPORTANT: SQL MUST return exactly these column aliases:
    1. 'category' (TEXT)
    2. 'value' (INT)

    Example:
    SELECT district as category, COUNT(*) as value FROM patients GROUP BY district

    sensitivity: IQR multiplier (1.0=loose, 1.5=moderate, 2.0=strict)
    """
    global _last_anomaly_data
    from backend.anomaly_detection import detect_spatial_anomalies
    from backend.forecast_trend import ForecastError

    df, err = _db.execute(sql)
    if err:
        return f"SQL Error: {err}"
    if df is None or df.empty:
        return "No data for outlier detection"

    try:
        result = detect_spatial_anomalies(
            df=df,
            multiplier=sensitivity,
        )

        _last_anomaly_data = result

        if result["total"] == 0:
            msg = (
                f"No outliers detected ({result['total_categories']} categories)\n"
                f"Baseline: median={result['baseline_median']} "
                f"(Q1={result['baseline_q1']}, Q3={result['baseline_q3']})"
            )
        else:
            msg = (
                f"Geographic Outlier Detection (IQR method)\n"
                f"Baseline: median={result['baseline_median']} "
                f"(Q1={result['baseline_q1']}, Q3={result['baseline_q3']})\n"
                f"Found {result['total']} outliers:\n\n"
            )
            # I'm showing off a bit, but it might look really good.
            for anomaly in result["anomalies"]:
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MODERATE": "🟡", "LOW": "⚪"}.get(anomaly["severity"], "⚪")

                arrow = "↑" if anomaly["direction"] == "above" else "↓"

                msg += (
                    f"{icon} {anomaly['category']}: {anomaly['value']} "
                    f"(median={anomaly['median']}, {arrow}{abs(anomaly['deviation']):.0f}, "
                    f"+{anomaly['relative_deviation']}%, {anomaly['severity']})\n"
                )

        if result.get("warnings"):
            msg += "\n⚠️ " + "\n".join(result["warnings"][:2])

        return msg

    except ForecastError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


@tool
def analyze_health_trends(target: str) -> str:
    """
    Analyzes a specific disease class or code for Seasonality, Geography, Demographics, and Trends.

    Args:
        target: A known group name (e.g., 'ORVI', 'Diabetes') OR a specific ICD root code (e.g., 'J00', 'I10').
                Use this to find peaks, demographic skews, and district anomalies.
    """
    target_codes = _classifier.get_target_codes(target)
    if not target_codes:
        return f"Could not find definitions for '{target}'. Try searching for codes first."

    code_list_str = "', '".join(target_codes)

    sql = f"""
    SELECT
        p.prescription_id,
        p.date,
        p.year,
        p.month,
        pt.birth_dt,
        pt.gender,
        pt.district,
        d.diagnosis_name
    FROM prescriptions p
    JOIN patients pt ON p.patient_id = pt.patient_id
    JOIN diagnoses d ON p.diagnosis_code = d.diagnosis_code
    WHERE SUBSTR(p.diagnosis_code, 1, 3) IN ('{code_list_str}')
    """

    df, err = _db.execute(sql)
    if err: return f"Database Error: {err}"
    if df is None or df.empty: return f"No records found for {target}."

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['birth_dt'] = pd.to_datetime(df['birth_dt'], dayfirst=True, errors='coerce')
    df['age'] = df['year'] - df['birth_dt'].dt.year
    df = df[(df['age'] >= 0) & (df['age'] <= 120)]

    total_cases = len(df)

    monthly = df.groupby('month').size()
    monthly_pct = (monthly / total_cases * 100).round(1)

    winter_sum = monthly_pct.loc[monthly_pct.index.isin([10,11,12,1,2])].sum()
    summer_sum = monthly_pct.loc[monthly_pct.index.isin([6,7,8])].sum()

    season_insight = "No strong seasonality."
    if winter_sum > 55: season_insight = f"Winter Peak ({winter_sum:.1f}% cases in Oct-Feb)."
    if summer_sum > 40: season_insight = f"Summer Peak ({summer_sum:.1f}% cases in Jun-Aug)."

    avg_age = df['age'].mean()
    gender_counts = df['gender'].value_counts(normalize=True)
    female_pct = gender_counts.get('Ж', 0) * 100

    demo_insight = "Balanced demographics."
    if female_pct > 70: demo_insight = f"Predominantly Female ({female_pct:.1f}%)."
    elif female_pct < 30: demo_insight = f"Predominantly Male ({(100-female_pct):.1f}%)."

    if avg_age > 60: demo_insight += " Affects Elderly."
    elif avg_age < 18: demo_insight += " Affects Children."


    dist_counts = df['district'].value_counts(normalize=True) * 100
    top_dist = dist_counts.head(1)
    geo_insight = f"Top district: {top_dist.index[0]} ({top_dist.values[0]:.1f}%)."

    trend_insight = "Stable"
    if df['date'].notna().sum() > 10:
        ts = df.set_index('date').resample('W').size().fillna(0)
        if len(ts) > 4:
            # Simple linear regression on last 12 weeks
            y = ts.iloc[-12:].values
            x = np.arange(len(y))
            if np.mean(y) > 0:
                slope, _ = np.polyfit(x, y, 1)
                norm_slope = slope / np.mean(y)
                if norm_slope > 0.05: trend_insight = "Growing"
                elif norm_slope < -0.05: trend_insight = "Declining"

    report = {
        "target": target,
        "total_cases": int(total_cases),
        "seasonality": {
            "insight": season_insight,
            "winter_share_pct": round(winter_sum, 1)
        },
        "demographics": {
            "insight": demo_insight,
            "avg_age": round(avg_age, 1),
            "female_pct": round(female_pct, 1)
        },
        "geography": {
            "insight": geo_insight
        },
        "trend": trend_insight
    }

    return json.dumps(report, ensure_ascii=False, indent=2)

@tool
def list_disease_groups() -> str:
    """Returns the list of available pre-defined disease groups (like 'ORVI', 'Diabetes') for analysis."""
    groups = _classifier.get_groups()
    return json.dumps(groups, ensure_ascii=False, indent=2)


"""
@tool
def detect_frequency_anomalies(sql: str) -> str:
    docstring
    Detect items with anomalous frequencies (over/underrepresented).

    SQL must return: 'item' (TEXT), 'count' (INT).
    Needs 10+ items. Use for diagnosis/drug frequency analysis.

    Example SQL:
        SELECT diagnosis_code as item, COUNT(*) as count
        FROM prescriptions
        GROUP BY diagnosis_code
    docstring

    global _last_anomaly_data

    # TODO: Implementation
    pass
"""

TOOLS = [
    search_codes,
    run_sql,
    forecast_trend,
    create_visualization,
    detect_outbreak,
    detect_geographic_outliers,
    analyze_health_trends,
    list_disease_groups,
    # detect_frequency_anomalies,
]
