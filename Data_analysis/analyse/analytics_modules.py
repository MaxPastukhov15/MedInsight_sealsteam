import pandas as pd
import numpy as np
import os

def analyze_trend_pipeline(df_subset):
    """
    Implements the requested 6-step pipeline:
    Resample -> Rolling -> Peaks -> Seasonality -> Trend Direction
    """
    # 1. Prepare Time Series (Weekly Resample)
    # Weekly is cleaner than Daily for medical data (removes weekend drops)
    ts = df_subset.set_index('date').resample('W').size().fillna(0)

    # 2. Rolling Mean (4 weeks)
    rolling_mean = ts.rolling(window=4).mean().fillna(0)

    # 3. Detect Peaks
    # Threshold: Mean + 1.5 * StdDev
    # Note: We calculate stats on the *whole* series to find global anomalies.
    global_mean = ts.mean()
    global_std = ts.std()
    threshold = global_mean + (1.5 * global_std)

    peaks = ts[ts > threshold]
    peak_list = [{"date": str(d.date()), "value": int(v)} for d, v in peaks.items()]

    # 4. Seasonality (Monthly)
    temp_df = pd.DataFrame({'cases': ts})
    temp_df['month'] = temp_df.index.month
    seasonality_series = temp_df.groupby('month')['cases'].mean()

    avg_annual = seasonality_series.mean()
    seasonality_data = []
    for m in range(1, 13):
        val = seasonality_series.get(m, 0.0)
        status = "High" if val > avg_annual else "Normal"
        seasonality_data.append({
            "month": int(m),
            "avg_cases_per_week": round(val, 2),
            "status": status
        })

    # 5. Trend Direction (Linear Regression on last N points)
    # Window: Last 12 weeks (~3 months)
    last_n = 12
    trend_direction = "Stable"

    if len(ts) >= last_n:
        y = ts.iloc[-last_n:].values
        x = np.arange(len(y))

        # Fit line: y = mx + c
        if np.all(y == 0):
            slope = 0
        else:
            slope, _ = np.polyfit(x, y, 1)

        # We normalize slope relative to the mean to make it scale-independent
        # e.g., if mean is 100, a slope of 1 is small. If mean is 1, slope of 1 is huge.
        mean_y = np.mean(y) if np.mean(y) > 0 else 1
        norm_slope = slope / mean_y

        if norm_slope > 0.05:
            trend_direction = "Growing"
        elif norm_slope < -0.05:
            trend_direction = "Declining"

    # 6. Timeline Construction
    timeline = []
    for date_idx, val in ts.items():
        r_val = rolling_mean.loc[date_idx]
        timeline.append({
            "date": str(date_idx.date()),
            "cases": int(val),
            "rolling_mean": round(float(r_val), 2)
        })

    return {
        "trend_direction": trend_direction,
        "seasonality": seasonality_data,
        "peaks": peak_list,
        "timeline": timeline
    }

def get_geography_anomalies(df):
    """
    Finds districts where a specific disease class is disproportionately high.
    Returns JSON-ready list.
    """
    if 'disease_class' not in df.columns:
        return []

    geo_counts = df.groupby(['district', 'disease_class']).size().unstack(fill_value=0)

    # Normalization
    district_totals = geo_counts.sum(axis=1)
    district_shares = geo_counts.div(district_totals, axis=0)
    city_totals = df['disease_class'].value_counts(normalize=True)

    anomalies = []

    for district in district_shares.index:
        diff = district_shares.loc[district] - city_totals

        significant = diff[diff > 0.05].sort_values(ascending=False)

        for disease_cls, score in significant.items():
            anomalies.append({
                "district": district,
                "disease_class": disease_cls,
                "district_share_pct": round(district_shares.loc[district, disease_cls] * 100, 2),
                "city_avg_pct": round(city_totals[disease_cls] * 100, 2),
                "excess_pct": round(score * 100, 2)
            })

    return sorted(anomalies, key=lambda x: x['excess_pct'], reverse=True)

def get_demographic_insights(df):
    """
    Aggregates demographic stats for Root Codes and finds outliers.
    """
    stats = df.groupby(['root_code', 'root_name']).agg({
        'age': 'mean',
        'gender': lambda x: (x == 'Ж').mean(), # Female ratio
        'patient_id': 'count'
    }).rename(columns={'patient_id': 'count'})

    # Filter for statistical significance (> 300 cases)
    stats = stats[stats['count'] > 300].reset_index()

    insights = {
        "elderly_diseases": [],
        "youth_diseases": [],
        "female_diseases": [],
        "male_diseases": []
    }

    def format_row(row):
        return {
            "code": row['root_code'],
            "name": row['root_name'],
            "avg_age": round(row['age'], 1),
            "female_pct": round(row['gender'] * 100, 1),
            "total_cases": int(row['count'])
        }

    # 1. Elderly
    top_elderly = stats.sort_values('age', ascending=False).head(5)
    insights['elderly_diseases'] = [format_row(r) for _, r in top_elderly.iterrows()]

    # 2. Youth
    top_youth = stats.sort_values('age', ascending=True).head(5)
    insights['youth_diseases'] = [format_row(r) for _, r in top_youth.iterrows()]

    # 3. Female
    female = stats[stats['gender'] > 0.85].sort_values('count', ascending=False).head(10)
    insights['female_diseases'] = [format_row(r) for _, r in female.iterrows()]

    # 4. Male
    male = stats[stats['gender'] < 0.15].sort_values('count', ascending=False).head(10)
    insights['male_diseases'] = [format_row(r) for _, r in male.iterrows()]

    return insights