"""
Generate a reproducible synthetic, zone-day dataset for an academic forecasting project.

All records are simulated. Coordinates are fictional grid coordinates and do not
represent real ATM locations or actual crime incidents.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_ZONES = 12
N_DAYS = 540
START_DATE = "2025-01-01"

def generate_dataset(output_path="data/raw/synthetic_atm_data.csv"):
    rng = np.random.default_rng(SEED)
    dates = pd.date_range(START_DATE, periods=N_DAYS, freq="D")
    # Fictional coordinates around an arbitrary origin; these are not real locations.
    zone_lat = 31.0 + np.repeat(np.arange(3), 4) * 0.025 + rng.normal(0, 0.003, N_ZONES)
    zone_lon = 75.0 + np.tile(np.arange(4), 3) * 0.025 + rng.normal(0, 0.003, N_ZONES)
    zone_activity = rng.uniform(0.75, 1.35, N_ZONES)
    zone_risk = rng.uniform(0.65, 1.55, N_ZONES)

    records = []
    for z in range(N_ZONES):
        for i, date in enumerate(dates):
            dow = date.dayofweek
            weekend = int(dow >= 5)
            month = date.month
            hour_peak = 1.0 + 0.12 * (dow in [4, 5]) + 0.08 * (month in [10, 11, 12])
            withdrawal_count = int(rng.poisson(75 * zone_activity[z] * hour_peak))
            avg_withdrawal_amount = float(np.clip(rng.normal(2600 + 250 * zone_activity[z], 650), 500, 6500))
            total_withdrawal_amount = withdrawal_count * avg_withdrawal_amount
            unusual_activity = int(rng.binomial(max(withdrawal_count, 1), min(0.025 * zone_risk[z], 0.12)))
            # A simulated daily incident-generating process with zone and calendar effects.
            seasonal = 1 + 0.18 * np.sin(2 * np.pi * i / 30.0)
            weekend_factor = 1.12 if weekend else 1.0
            rate = (0.34 * zone_risk[z] * seasonal * weekend_factor
                    + 0.012 * unusual_activity + 0.000002 * withdrawal_count)
            incident_count = int(rng.poisson(max(rate, 0.03)))
            records.append({
                "zone_id": f"ZONE_{z+1:02d}",
                "date": date,
                "latitude": zone_lat[z],
                "longitude": zone_lon[z],
                "day_of_week": dow,
                "month": month,
                "is_weekend": weekend,
                "atm_count": int(rng.integers(3, 13)),
                "withdrawal_count": withdrawal_count,
                "avg_withdrawal_amount": round(avg_withdrawal_amount, 2),
                "total_withdrawal_amount": round(total_withdrawal_amount, 2),
                "unusual_activity_count": unusual_activity,
                "cashout_incident_count": incident_count,
            })

    daily = pd.DataFrame(records).sort_values(["zone_id", "date"]).reset_index(drop=True)
    grouped = daily.groupby("zone_id", group_keys=False)

    # All predictors are historical: shift(1) ensures the current day's outcomes
    # are not used to predict the future target.
    for window in [7, 30]:
        daily[f"withdrawals_sum_{window}d"] = grouped["withdrawal_count"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=window).sum()
        )
        daily[f"unusual_activity_sum_{window}d"] = grouped["unusual_activity_count"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=window).sum()
        )
        daily[f"incidents_sum_{window}d"] = grouped["cashout_incident_count"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=window).sum()
        )

    # Target: incidents in the NEXT seven days, excluding the current date.
    daily["target_incidents_next_7d"] = grouped["cashout_incident_count"].transform(
        lambda s: s.shift(-1).rolling(7, min_periods=7).sum().shift(-6)
    )
    # The expression above is aligned to the current date: sum(t+1 ... t+7).
    daily["target_incidents_next_7d"] = daily["target_incidents_next_7d"].astype("float")
    daily["target_risk"] = pd.cut(
        daily["target_incidents_next_7d"],
        bins=[-0.1, 1, 3, np.inf],
        labels=["Low", "Medium", "High"]
    )

    daily = daily.dropna(subset=[
        "withdrawals_sum_30d", "unusual_activity_sum_30d",
        "incidents_sum_30d", "target_incidents_next_7d", "target_risk"
    ]).copy()
    daily["target_incidents_next_7d"] = daily["target_incidents_next_7d"].astype(int)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(output, index=False)
    print(f"Saved {len(daily):,} rows to {output}")
    print("\nRisk label distribution:")
    print(daily["target_risk"].value_counts())
    print("\nDate range:", daily["date"].min(), "to", daily["date"].max())
    return daily

if __name__ == "__main__":
    generate_dataset()
