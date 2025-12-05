import json
from datetime import datetime
from dataframe import get_master_dataframe, NpEncoder
from analytics_modules import *

if __name__ == "__main__":
    full_df = get_master_dataframe()
    total_records = len(full_df)

    top_codes = full_df['root_code'].value_counts().head(10).index.tolist()

    final_output = {
        "meta": {
            "generated_at": str(datetime.now()),
            "total_records_analyzed": total_records,
            "top_diseases_analyzed": top_codes
        },
        "geographic_anomalies": get_geography_anomalies(full_df),
        "demographic_insights": get_demographic_insights(full_df),
        "disease_trends": {}
    }

    print(f"Running Trend Pipeline for top {len(top_codes)} diseases...")

    for code in top_codes:
        subset = full_df[full_df['root_code'] == code].copy()

        # Get readable name (first one found)
        name = subset['root_name'].iloc[0]

        print(f"  > Analyzing {code} ({name})...")

        trend_data = analyze_trend_pipeline(subset)

        final_output["disease_trends"][code] = {
            "name": name,
            "stats": trend_data
        }

    output_filename = "insights_report.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4, cls=NpEncoder)

    print(f"\nSuccess! Insights saved to '{output_filename}'")