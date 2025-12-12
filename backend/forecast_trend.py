import warnings
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
import numpy as np

try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class ForecastError(Exception):
    """Custom exception for forecasting errors."""

    pass


def calculate_ensemble_weights(days: int) -> Tuple[float, float]:
    """
    Calculate adaptive weights for SARIMA and Prophet based on forecast horizon.

    Args:
        days: Forecast horizon in days (14-90)

    Returns:
        (sarima_weight, prophet_weight) tuple summing to 1.0
    """
    # Normalize days to [0, 1] range: 14 days -> 0, 90 days -> 1
    normalized = (days - 14) / (90 - 14)
    normalized = max(0.0, min(1.0, normalized))

    # SARIMA: starts at 0.7 (14 days), decreases to 0.3 (90 days)
    sarima_weight = 0.7 - 0.4 * normalized

    # Prophet: starts at 0.3 (14 days), increases to 0.7 (90 days)
    prophet_weight = 1.0 - sarima_weight

    return sarima_weight, prophet_weight


def validate_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate and prepare DataFrame for forecasting.

    Args:
        df: DataFrame with 'date' and 'cases' columns

    Returns:
        Tuple of (validated_df, warnings_list)

    Raises:
        ForecastError: If validation fails critically
    """
    warnings_list = []

    # Check required columns
    if "date" not in df.columns or "cases" not in df.columns:
        raise ForecastError(f"DataFrame must have 'date' and 'cases' columns. Got: {list(df.columns)}")

    # Convert date column to datetime
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        raise ForecastError(f"Failed to parse 'date' column: {e}")

    # Convert cases to numeric
    try:
        df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
    except Exception as e:
        raise ForecastError(f"Failed to parse 'cases' column: {e}")

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    # Check for duplicate dates
    duplicates = df["date"].duplicated().sum()
    if duplicates > 0:
        warnings_list.append(f"Found {duplicates} duplicate dates, aggregated by sum")
        df = df.groupby("date", as_index=False)["cases"].sum()  # type: ignore

    return df, warnings_list


def fill_missing_dates(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Fills missing dates in a time series using a hybrid adaptive strategy.

    The function regularizes the time series to a daily frequency and fills gaps based on their duration:
    1. Small gaps (<= 3 days): Linear Interpolation.
       Rationale: Short absences are likely random noise or weekends; trend continuity is assumed.
    2. Large gaps (> 3 days): Forward Fill (Last Observation Carried Forward).
       Rationale: Long absences indicate structural issues; inventing trends via interpolation is risky
       in medical contexts (hallucination risk).

    Args:
        df: Input DataFrame containing 'date' (datetime) and 'cases' (numeric) columns.

    Returns:
        Tuple[pd.DataFrame, List[str]]:
            - Processed DataFrame with continuous daily dates and filled values.
            - List of execution warnings/logs describing the actions taken.
    """
    warnings_list: list[str] = []

    if df.empty:
        return df, ["Warning: Input DataFrame is empty."]

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Reindex to ensure complete daily frequency
    df = df.set_index("date").asfreq("D")
    df.index.name = "date"

    total_missing = df["cases"].isna().sum()
    if total_missing == 0:
        return df.reset_index(), warnings_list

    # Identify and measure gaps
    is_missing = df["cases"].isna()

    gap_groups = (is_missing != is_missing.shift()).cumsum()
    gap_sizes = df.groupby(gap_groups)["cases"].transform("size")

    # Define Masks for different strategies
    small_gaps_mask = is_missing & (gap_sizes <= 3)
    large_gaps_mask = is_missing & (gap_sizes > 3)

    n_small = small_gaps_mask.sum()
    n_large = large_gaps_mask.sum()

    if n_small > 0:
        warnings_list.append(f"Interpolated {n_small} days (gaps <= 3 days)")
    if n_large > 0:
        warnings_list.append(f"Forward-filled {n_large} days (gaps > 3 days)")

    # Strategy A: Linear Interpolation for small gaps
    if n_small > 0:
        interpolated_series = df["cases"].interpolate(method="linear")
        df.loc[small_gaps_mask, "cases"] = interpolated_series[small_gaps_mask]

    # Strategy B: Forward Fill for large gaps
    if n_large > 0:
        ffilled_series = df["cases"].ffill()
        df.loc[large_gaps_mask, "cases"] = ffilled_series[large_gaps_mask]

    # Edge сase handling
    if df["cases"].isna().any():
        warnings_list.append("Backward-filled leading missing values")
        df["cases"] = df["cases"].bfill()

    df["cases"] = df["cases"].fillna(0)

    df = df.reset_index()

    return df, warnings_list


def forecast_with_prophet(
    df: pd.DataFrame, days: int, enable_yearly_seasonality: Optional[bool] = None
) -> pd.DataFrame:
    """
    Generate forecast using Prophet.

    Args:
        df: DataFrame with 'date' and 'cases' columns
        days: Number of days to forecast
        enable_yearly_seasonality: Force yearly seasonality (None=auto)

    Returns:
        DataFrame with columns: date, predicted, lower_bound, upper_bound

    Raises:
        ForecastError: If Prophet is not available or forecast fails
    """
    if not PROPHET_AVAILABLE:
        raise ForecastError("Prophet not installed. Run: pip install prophet")

    try:
        prophet_df = df[["date", "cases"]].copy()
        prophet_df.columns = ["ds", "y"]

        data_span_days = (df["date"].max() - df["date"].min()).days

        # Auto-detect yearly seasonality if not specified
        if enable_yearly_seasonality is None:
            yearly_seasonality = data_span_days >= 730
        else:
            yearly_seasonality = enable_yearly_seasonality

        model = Prophet(
            growth="linear",
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=yearly_seasonality,
            seasonality_mode="multiplicative",
            changepoint_prior_scale=0.05,
            interval_width=0.95,
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(prophet_df)

        # Create future dataframe
        future = model.make_future_dataframe(periods=days, freq="D" if days < 60 else "W")
        # Ensure frequency matches data if aggregated
        if len(df) > 1:
            dt1 = df["date"].iloc[1]
            dt0 = df["date"].iloc[0]
            delta = dt1 - dt0
            if delta.days >= 28:
                future = model.make_future_dataframe(periods=days, freq="MS")
            elif delta.days >= 6:
                future = model.make_future_dataframe(periods=days, freq="W-MON")
            else:
                future = model.make_future_dataframe(periods=days, freq="D")

        forecast = model.predict(future)
        forecast = forecast[forecast["ds"] > df["date"].max()]

        result = pd.DataFrame(
            {
                "date": forecast["ds"],
                "predicted": forecast["yhat"],
                "lower_bound": forecast["yhat_lower"],
                "upper_bound": forecast["yhat_upper"],
            }
        ).reset_index(drop=True)

        return result

    except Exception as e:
        raise ForecastError(f"Prophet forecast failed: {str(e)}")


def forecast_with_sarima(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Generate forecast using SARIMAX (Seasonal ARIMA).

    Args:
        df: DataFrame with 'date' and 'cases' columns
        days: Number of days to forecast

    Returns:
        DataFrame with columns: date, predicted, lower_bound, upper_bound

    Raises:
        ForecastError: If statsmodels is not available or forecast fails
    """
    if not STATSMODELS_AVAILABLE:
        raise ForecastError("statsmodels not installed. Run: pip install statsmodels")

    try:
        ts = df.set_index("date")["cases"]

        # Detect seasonality period based on index frequency
        freq = pd.infer_freq(ts.index)  # type: ignore
        seasonal_period = 7

        if freq:
            if "W" in freq:
                seasonal_period = 52
            elif "M" in freq:
                seasonal_period = 12

        model = SARIMAX(
            ts,
            order=(1, 1, 1),
            seasonal_order=(1, 0, 1, seasonal_period),
            enforce_stationarity=False,  # Better convergence
            enforce_invertibility=False,
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fitted = model.fit(disp=False, maxiter=200)

        # Generate forecast
        forecast = fitted.get_forecast(steps=days)
        forecast_df = forecast.summary_frame(alpha=0.05)  # 95% CI

        last_date = df["date"].max()

        # Determine frequency for future dates
        future_freq = "D"
        if len(df) > 1:
            dt1 = df["date"].iloc[1]
            dt0 = df["date"].iloc[0]
            delta = dt1 - dt0
            if delta.days >= 28:
                future_freq = "MS"
            elif delta.days >= 6:
                future_freq = "W-MON"

        future_dates = pd.date_range(
            start=last_date + timedelta(days=1) if future_freq == "D" else last_date,
            periods=days + 1 if future_freq != "D" else days,
            freq=future_freq,
        )
        # If aggregation, start from next period
        if future_freq != "D":
            future_dates = future_dates[1:]

        result = pd.DataFrame(
            {
                "date": future_dates[:days],
                "predicted": forecast_df["mean"].values,
                "lower_bound": forecast_df["mean_ci_lower"].values,
                "upper_bound": forecast_df["mean_ci_upper"].values,
            }
        )

        return result

    except Exception as e:
        raise ForecastError(f"SARIMA forecast failed: {str(e)}")


def calculate_confidence(forecast_df: pd.DataFrame) -> str:
    """
    Calculate confidence level based on prediction interval width.

    Confidence tiers based on relative interval width:
    - High: interval < 30% of predicted value (tight bounds)
    - Medium: interval 30-60% of predicted value
    - Low: interval > 60% of predicted value (wide uncertainty)

    Args:
        forecast_df: DataFrame with predicted, lower_bound, upper_bound columns

    Returns:
        "high", "medium", or "low"
    """
    # Calculate average interval width
    interval_width = (forecast_df["upper_bound"] - forecast_df["lower_bound"]).mean()

    # Calculate relative width (as percentage of predicted value)
    avg_predicted = forecast_df["predicted"].mean()
    if avg_predicted == 0 or np.isnan(avg_predicted):
        return "low"

    relative_width = interval_width / avg_predicted

    # Classify confidence
    if relative_width < 0.3:
        return "high"
    elif relative_width < 0.6:
        return "medium"
    else:
        return "low"


def generate_forecast(
    df: pd.DataFrame,
    days: int = 30,
    max_history_days: Optional[int] = None,
    enable_yearly_seasonality: Optional[bool] = None,
    use_ensemble: bool = True,
    auto_aggregate: bool = True,
) -> Dict[str, Any]:
    """
    Main forecasting function with automatic model selection, ensemble, and smart aggregation.

    Workflow:
    1. Validate and prepare data
    2. Apply Smart Aggregation (Day -> Week/Month) based on data density
    3. Fill missing dates
    4. Train Prophet and/or SARIMA models
    5. Create adaptive ensemble if both available
    6. Post-process: clip negatives, round to integers
    7. Calculate confidence intervals

    Args:
        df: DataFrame with 'date' and 'cases' columns
        days: Forecast horizon (14-90 days)
        max_history_days: Limit historical data to last N days (None=all)
        enable_yearly_seasonality: Force yearly seasonality for Prophet (None=auto)
        use_ensemble: Use ensemble if both models available
        auto_aggregate: Automatically aggregate sparse data (default True)

    Returns:
        Dictionary with forecast results and metadata:
        {
            "forecast": [{"date": str, "predicted": int, ...}, ...],
            "model_confidence": "high"|"medium"|"low",
            "model_used": "prophet"|"sarima"|"ensemble",
            "data_quality": {"input_days": int, "gaps_filled": int, "warnings": [...]}
        }

    Raises:
        ForecastError: If forecast generation fails
    """
    warnings_list = []

    if days < 14 or days > 365:
        raise ForecastError(f"Forecast horizon must be 14-365 days, got {days}")

    df, val_warnings = validate_dataframe(df)
    warnings_list.extend(val_warnings)

    aggregation_mode = "day"

    if auto_aggregate:
        # Calculate data density (average cases per day)
        total_cases = df["cases"].sum()
        total_span = (df["date"].max() - df["date"].min()).days + 1
        avg_daily_cases = total_cases / total_span if total_span > 0 else 0

        # Decision logic based on sparsity thresholds
        if avg_daily_cases < 0.5:
            aggregation_mode = "month"
        elif avg_daily_cases < 20.0:
            aggregation_mode = "week"

        # Apply aggregation if needed
        if aggregation_mode != "day":
            df["date"] = pd.to_datetime(df["date"])

            if aggregation_mode == "week":
                rule = "W-MON"
                divisor = 7
            else:  # month
                rule = "MS"
                divisor = 30

            time_span_days = (df["date"].max() - df["date"].min()).days
            df = df.set_index("date").resample(rule).sum().reset_index()

            warnings_list.append(
                f"Auto-aggregation ({aggregation_mode}): density {avg_daily_cases:.2f} cases/day. "
                f"Data spanning {time_span_days} days aggregated into {len(df)} {aggregation_mode}s."
            )

            # Adjust horizon to new units
            original_days = days
            days = max(1, days // divisor)

            warnings_list.append(f"Forecast horizon adjusted: {original_days} days → {days} {aggregation_mode}s")

    # Limit historical data if requested
    if max_history_days is not None and max_history_days > 0:
        cutoff_date = df["date"].max() - timedelta(days=max_history_days)
        original_len = len(df)
        df = df[df["date"] > cutoff_date]
        if len(df) < original_len:
            warnings_list.append(f"Limited history to last {max_history_days} days ({len(df)} records)")

    # Check minimum data requirement (adjusted for aggregation)
    min_required = max(10, days // 2)
    if len(df) < min_required:
        raise ForecastError(
            f"Insufficient data: got {len(df)} {aggregation_mode}s, need at least {min_required} for forecast."
        )

    # Fill missing dates (using new frequency)
    if aggregation_mode == "day":
        df, fill_warnings = fill_missing_dates(df)
        warnings_list.extend(fill_warnings)
    else:
        # For aggregated data, ensure continuity
        idx = pd.date_range(
            start=df["date"].min(), end=df["date"].max(), freq="W-MON" if aggregation_mode == "week" else "MS"
        )
        df = df.set_index("date").reindex(idx, fill_value=0).reset_index()
        df.columns = ["date", "cases"]

    models_available = []
    if PROPHET_AVAILABLE:
        models_available.append("prophet")
    if STATSMODELS_AVAILABLE:
        models_available.append("sarima")

    if not models_available:
        raise ForecastError("No forecasting libraries available. Install: pip install prophet statsmodels")

    forecasts = {}

    if PROPHET_AVAILABLE:
        try:
            forecasts["prophet"] = forecast_with_prophet(df, days, enable_yearly_seasonality)
        except ForecastError as e:
            warnings_list.append(f"Prophet failed: {str(e)}")

    if STATSMODELS_AVAILABLE:
        try:
            forecasts["sarima"] = forecast_with_sarima(df, days)
        except ForecastError as e:
            warnings_list.append(f"SARIMA failed: {str(e)}")

    if not forecasts:
        raise ForecastError("All forecasting models failed. Check warnings for details.")

    if len(forecasts) == 2 and use_ensemble:
        effective_days = days * (7 if aggregation_mode == "week" else 30 if aggregation_mode == "month" else 1)
        sarima_weight, prophet_weight = calculate_ensemble_weights(effective_days)

        ensemble = forecasts["sarima"].copy()
        ensemble["predicted"] = (
            sarima_weight * forecasts["sarima"]["predicted"] + prophet_weight * forecasts["prophet"]["predicted"]
        )
        ensemble["lower_bound"] = (
            sarima_weight * forecasts["sarima"]["lower_bound"] + prophet_weight * forecasts["prophet"]["lower_bound"]
        )
        ensemble["upper_bound"] = (
            sarima_weight * forecasts["sarima"]["upper_bound"] + prophet_weight * forecasts["prophet"]["upper_bound"]
        )

        final_forecast = ensemble
        model_used = "ensemble"
        warnings_list.append(f"Ensemble weights: SARIMA {sarima_weight:.1%}, Prophet {prophet_weight:.1%}")
    else:
        model_used = list(forecasts.keys())[0]
        final_forecast = forecasts[model_used]

    # Post-processing:
    final_forecast["predicted"] = final_forecast["predicted"].clip(lower=0).round().astype(int)
    final_forecast["lower_bound"] = final_forecast["lower_bound"].clip(lower=0).round().astype(int)
    final_forecast["upper_bound"] = final_forecast["upper_bound"].clip(lower=0).round().astype(int)

    # Calculate confidence
    confidence = calculate_confidence(final_forecast)

    forecast_list = []
    for _, row in final_forecast.iterrows():
        forecast_list.append(
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "predicted": int(row["predicted"]),
                "lower_bound": int(row["lower_bound"]),
                "upper_bound": int(row["upper_bound"]),
            }
        )

    return {
        "forecast": forecast_list,
        "model_confidence": confidence,
        "model_used": model_used,
        "data_quality": {"input_days": len(df), "aggregation": aggregation_mode, "warnings": warnings_list},
    }
