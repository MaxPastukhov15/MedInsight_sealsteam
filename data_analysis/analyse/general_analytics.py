from dataframe import get_master_dataframe


def analyze_seasonality(df):
    """
    Finds seasonal peaks.
    """
    print("\n--- ANALYZING SEASONALITY ---")

    # Filter for groups with at least 500 cases total
    group_counts = df["root_code"].value_counts()
    significant_groups = group_counts[group_counts > 500].index

    subset = df[df["root_code"].isin(significant_groups)]

    matrix = subset.groupby(["root_name", "month"]).size().unstack(fill_value=0)

    # Normalize to percentages
    pct_matrix = matrix.div(matrix.sum(axis=1), axis=0)

    winter_cols = [c for c in [10, 11, 12, 1, 2] if c in pct_matrix.columns]
    pct_matrix["winter_sum"] = pct_matrix[winter_cols].sum(axis=1)

    top_winter = pct_matrix.sort_values("winter_sum", ascending=False).head(5)

    print("\n--- Top Winter Diseases (Oct-Feb) ---")
    for name, row in top_winter.iterrows():
        print(f"  {name}: {row['winter_sum']:.1%} of annual cases")

    summer_cols = [c for c in [6, 7, 8] if c in pct_matrix.columns]
    pct_matrix["summer_sum"] = pct_matrix[summer_cols].sum(axis=1)

    top_summer = pct_matrix.sort_values("summer_sum", ascending=False).head(5)

    print("\n--- Top Summer Diseases (Jun-Aug) ---")
    for name, row in top_summer.iterrows():
        print(f"  {name}: {row['summer_sum']:.1%} of annual cases")


def analyze_geography(df):
    """
    Analyzes geography at the highest level: Disease Class.
    Example: 'Infectious Diseases' vs 'Respiratory Diseases' in specific districts.
    """
    print("\n--- ANALYZING GEOGRAPHY ---")

    if "disease_class" not in df.columns:
        print("Column 'disease_class' not found. Skipping.")
        return

    geo_counts = df.groupby(["district", "disease_class"]).size().unstack(fill_value=0)

    # Normalize: Calculate the share of diseases WITHIN a district
    # (e.g., In Central District, 20% of all cases are Respiratory)
    district_totals = geo_counts.sum(axis=1)
    district_shares = geo_counts.div(district_totals, axis=0)

    # Compare against City Average
    city_totals = df["disease_class"].value_counts(normalize=True)

    print("Finding Anomalies (District vs City Average)...")

    for district in district_shares.index:
        diff = district_shares.loc[district] - city_totals
        # Filter: Finding where the district is > 5% higher than expected
        anomalies = diff[diff > 0.05].sort_values(ascending=False)

        if not anomalies.empty:
            print(f"\nDistrict: {district}")
            for disease_cls, score in anomalies.items():
                actual_share = district_shares.loc[district, disease_cls]
                avg_share = city_totals[disease_cls]
                print(f"  > {disease_cls}: {actual_share:.1%} (City Avg: {avg_share:.1%})")


def analyze_demographics(df):
    """
    Finds 'Women's diseases' or 'Elderly diseases' using Root Codes.
    """
    print("\n--- ANALYZING DEMOGRAPHICS ---")

    stats = (
        df.groupby("root_name")
        .agg({"age": "mean", "gender": lambda x: (x == "Ж").mean(), "prescription_id": "count"})
        .rename(columns={"prescription_id": "total_cases"})
    )

    # Filter noise
    stats = stats[stats["total_cases"] > 300]

    print("\n--- Most Common in Elderly (Highest Avg Age) ---")
    print(stats.sort_values("age", ascending=False)["age"].head(5))

    print("\n--- Predominantly Female (>85%) ---")
    print(stats[stats["gender"] > 0.85].index.tolist())

    print("\n--- Predominantly Male (<15% Female) ---")
    print(stats[stats["gender"] < 0.15].index.tolist())


def analyze_trends(df):
    """
    Checks which ROOT groups spiked in 2020.
    """
    print("\n--- ANALYZING YEARLY TRENDS ---")

    yearly = df.groupby(["diagnosis_name", "year"]).size().unstack(fill_value=0)

    # Find which year was the "Peak Year" for each disease
    peak_years = yearly.idxmax(axis=1)

    print("Peak Year Distribution (How many diseases peaked in each year?):")
    print(peak_years.value_counts().sort_index())

    # Specific highlight: What spiked in 2020?
    if 2019 in yearly.columns and 2020 in yearly.columns:
        growth_2020 = ((yearly[2020] - yearly[2019]) / yearly[2019].replace(0, 1)).sort_values(ascending=False)
        # Filter for diseases with at least 50 cases in 2020 to avoid "1 case to 5 cases = 400% growth"
        significant_growth = growth_2020[yearly[2020] > 50].head(5)

        print("\nHighest Growth Rates in 2020 (vs 2019):")
        for name, rate in significant_growth.items():
            print(f"  - {name}: +{rate:.1%} growth")


if __name__ == "__main__":
    df = get_master_dataframe()
    print(f"Loaded {len(df)} records.")
    print(
        f"Aggregated into {df['root_code'].nunique()} Root Categories (vs {df['diagnosis_code'].nunique()} raw codes)."
    )

    analyze_seasonality(df)
    analyze_geography(df)
    analyze_demographics(df)
    analyze_trends(df)
