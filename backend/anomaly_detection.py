"""Anomaly detection tools for medical data analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Literal, List, Tuple

from backend.forecast_trend import validate_dataframe, fill_missing_dates, ForecastError


def _validate_anomaly_dataframe(
    df: pd.DataFrame, required_columns: List[str]
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate DataFrame for anomaly detection.
    
    Args:
        df: Input DataFrame
        required_columns: List of required column names
        
    Returns:
        Tuple of (validated_df, warnings_list)
        
    Raises:
        ForecastError: If validation fails
    """
    warnings_list: List[str] = []
    
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ForecastError(
            f"Missing columns: {missing}. Got: {list(df.columns)}"
        )
    
    if df.empty:
        raise ForecastError("DataFrame is empty")
    
    return df, warnings_list


def _detect_outliers_iqr(values: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """
    Detect outliers using Interquartile Range method.
    
    Args:
        values: Numeric series
        multiplier: IQR multiplier (default 1.5)
        
    Returns:
        Boolean mask of outliers
    """
    if len(values) == 0:
        return pd.Series([], dtype=bool)
    
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    
    if iqr == 0:
        return pd.Series([False] * len(values), index=values.index)
    
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    return (values < lower_bound) | (values > upper_bound)


def detect_timeseries_anomalies(
    df: pd.DataFrame,
    threshold_sigma: float = 2.5,
    min_seasons: int = 2,
) -> Dict[str, Any]:
    """
    Detect temporal anomalies using STL decomposition.
    
    Args:
        df: DataFrame with 'date' and 'cases' columns
        threshold_sigma: Anomaly sensitivity (2.0=loose, 2.5=moderate, 3.0=strict)
        min_seasons: Minimum number of seasonal cycles required (default 2)
        
    Returns:
        Dict with anomalies, components, and statistics
        
    Raises:
        ForecastError: If data is insufficient or STL fails
    """
    from statsmodels.tsa.seasonal import STL
    from backend.forecast_trend import validate_dataframe, fill_missing_dates
    
    warnings_list: List[str] = []
    
    df, val_warnings = validate_dataframe(df)
    warnings_list.extend(val_warnings)
    
    if df["cases"].sum() == 0:
        raise ForecastError("All case values are zero, cannot detect anomalies")
    
    # Try to detect and preserve Monthly/Weekly frequency
    df = df.sort_values("date").reset_index(drop=True)
    
    median_days = 0.0
    if len(df) > 1:
        median_days = df["date"].diff().dropna().dt.days.median()
    
    target_freq = None
    if 28 <= median_days <= 32:
        target_freq = "MS"
    elif 6 <= median_days <= 8:
        target_freq = "W-MON"
        
    if target_freq:
        idx = pd.date_range(start=df["date"].min(), end=df["date"].max(), freq=target_freq)
        df = df.set_index("date").reindex(idx)
        df.index.name = "date"
        df = df.reset_index()
        
        if df["cases"].isna().any():
            warnings_list.append(f"Interpolated gaps in {target_freq} data")
            df["cases"] = df["cases"].interpolate(method="linear")
            df["cases"] = df["cases"].fillna(0)
    else:
        df, fill_warnings = fill_missing_dates(df)
        warnings_list.extend(fill_warnings)
    
    ts = df.set_index("date")["cases"]

    # Auto-detect period for seasonality
    freq = pd.infer_freq(ts.index)
    
    if freq:
        if 'D' in freq:
            period = 7
        elif 'W' in freq:
            period = 52
        elif 'M' in freq:
            period = 12
        else:
            period = 7
    else:
        if len(df) > 1:
            diffs = df["date"].diff().dropna()
            median_days = diffs.dt.days.median()
            
            if median_days <= 1:
                period = 7
            elif median_days <= 7:
                period = 52
            elif median_days >= 28:
                period = 12
            else:
                period = 7
        else:
            period = 7
    
    min_data_points = min_seasons * period
    use_stl = True

    if len(df) < min_data_points:
        use_stl = False
        if len(df) < 3:
            raise ForecastError(f"Insufficient data: {len(df)} points, need at least 3")
        warnings_list.append(f"Not enough data for STL ({len(df)} pts). Using Simple Z-score.")
    
    try:
        if use_stl:
            seasonal_window = int(period)
            if seasonal_window % 2 == 0: # must be odd for STL
                seasonal_window += 1
            if seasonal_window < 7: # Ensure minimum smoothing
                seasonal_window = 7

            stl = STL(ts, seasonal=seasonal_window, period=period, robust=True)
            result = stl.fit()
            
            trend = result.trend
            seasonal = result.seasonal
            residual = result.resid
            model_name = "STL decomposition"
        else:
            # Fallback: Simple deviation from mean
            mean_val = ts.mean()
            trend = pd.Series(mean_val, index=ts.index)
            seasonal = pd.Series(0, index=ts.index)
            residual = ts - mean_val
            model_name = "Simple Z-score (short data)"

        residual_std = residual.std()
        if residual_std == 0:
            residual_std = 1.0
            
        threshold = threshold_sigma * residual_std
        anomaly_mask = np.abs(residual) > threshold
        
        if anomaly_mask.sum() == 0:
            return {
                "type": "timeseries",
                "anomalies": [],
                "total": 0,
                "period": f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
                "data_points": len(df),
                "model": model_name,
                "threshold_sigma": threshold_sigma,
                "warnings": warnings_list,
            }
        
        # Build anomalies list
        anomalies: List[Dict[str, Any]] = []
        anomalies_resid = residual[anomaly_mask]
        for date, resid_val in anomalies_resid.items():
            actual_cases = int(ts.loc[date])
            expected_cases = int(trend.loc[date] + seasonal.loc[date])
            deviation = int(resid_val)
            z_score = float(resid_val / residual_std)
            
            abs_z = abs(z_score)
            if abs_z > 4.0:
                severity = "CRITICAL"
            elif abs_z > 3.5:
                severity = "HIGH"
            elif abs_z > 2.5:
                severity = "MODERATE"
            else:
                severity = "LOW"
            
            anomalies.append({
                "date": date.strftime("%Y-%m-%d"),
                "actual": actual_cases,
                "expected": expected_cases,
                "deviation": deviation,
                "z_score": round(z_score, 2),
                "severity": severity,
                "direction": "spike" if deviation > 0 else "drop",
            })
        
        # Sort by absolute z-score (most severe first)
        anomalies.sort(key=lambda x: abs(x["z_score"]), reverse=True)
        
        return {
            "type": "timeseries",
            "anomalies": anomalies,
            "total": len(anomalies),
            "period": f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
            "data_points": len(df),
            "model": "STL decomposition",
            "threshold_sigma": threshold_sigma,
            "components": {
                "trend": trend.tolist(),
                "seasonal": seasonal.tolist(),
                "residual": residual.tolist(),
                "dates": df["date"].dt.strftime("%Y-%m-%d").tolist(),
                "cases": df["cases"].tolist(),
                "anomaly_flags": anomaly_mask.tolist(),
            },
            "warnings": warnings_list,
        }
        
    except Exception as e:
        raise ForecastError(f"STL decomposition failed: {str(e)}")



def detect_spatial_anomalies(
    df: pd.DataFrame,
    multiplier: float = 1.5,
) -> Dict[str, Any]:
    """
    Detect spatial/categorical outliers using IQR method.
    
    Args:
        df: DataFrame with 'category' and 'value' columns
        multiplier: IQR multiplier (default 1.5 = standard, 2.0 = strict, 1.0 = loose)
        
    Returns:
        Dict with anomalies, statistics, and warnings
    """
    warnings_list: List[str] = []
    
    df, val_warnings = _validate_anomaly_dataframe(df, ["category", "value"])
    warnings_list.extend(val_warnings)
    
    try:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    except Exception as e:
        raise ForecastError(f"Failed to parse 'value' column: {e}")
    
    original_len = len(df)
    df = df.dropna(subset=["value"])
    if len(df) < original_len:
        warnings_list.append(
            f"Dropped {original_len - len(df)} rows with invalid values"
        )
    
    if len(df) < 3:
        raise ForecastError(
            f"Need at least 3 categories for outlier detection, got {len(df)}"
        )
    
    try:
        outlier_mask = _detect_outliers_iqr(df["value"], multiplier=multiplier)
    except Exception as e:
        raise ForecastError(f"Outlier detection failed: {str(e)}")
    
    outliers_df = df[outlier_mask].copy()
    
    mean_val = df["value"].mean()
    std_val = df["value"].std()
    median_val = df["value"].median()
    q1 = df["value"].quantile(0.25)
    q3 = df["value"].quantile(0.75)
    
    # Build anomalies list
    anomalies: List[Dict[str, Any]] = []
    for idx in outliers_df.index:
        category_name = str(outliers_df.loc[idx, "category"])
        value = float(outliers_df.loc[idx, "value"])
        deviation = value - median_val
        
        relative_dev = abs(deviation) / median_val if median_val > 0 else 0
        if relative_dev > 2.0:
            severity = "CRITICAL"
        elif relative_dev > 1.0:
            severity = "HIGH"
        elif relative_dev > 0.5:
            severity = "MODERATE"
        else:
            severity = "LOW"
        
        anomalies.append({
            "category": category_name,
            "value": int(value),
            "median": round(median_val, 1),
            "q1": round(q1, 1),
            "q3": round(q3, 1),
            "deviation": round(deviation, 1),
            "relative_deviation": round(relative_dev * 100, 1),
            "severity": severity,
            "direction": "above" if deviation > 0 else "below",
        })
    
    # Sort by absolute deviation
    anomalies.sort(key=lambda x: abs(x["deviation"]), reverse=True)
    
    return {
        "type": "spatial",
        "method": "iqr",
        "anomalies": anomalies,
        "total": len(anomalies),
        "baseline_median": round(median_val, 1),
        "baseline_q1": round(q1, 1),
        "baseline_q3": round(q3, 1),
        "total_categories": len(df),
        "multiplier": multiplier,
        "warnings": warnings_list,
    }


"""
def detect_distribution_anomalies(
    df: pd.DataFrame,
    min_expected_frequency: float = 0.01,
) -> Dict[str, Any]:
    docstring
    Detect items with anomalous frequencies.
    
    Returns dict with:
        - anomalies: [{item, count, frequency, expected, z_score, type}, ...]
        - total, total_items
        - warnings
    docstring
    # TODO: Implementation
    pass
"""