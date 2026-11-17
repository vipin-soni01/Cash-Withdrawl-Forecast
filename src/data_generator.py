
"""
Generate a reproducible synthetic, India-wide zone-day dataset.

All records are simulated. Coordinates are fictional points around
approximate city centres and do not represent real ATM locations
or actual crime incidents.
"""

from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_DAYS = 540
START_DATE = "2025-01-01"

# Approximate city-centre coordinates used only as fictional map anchors.
# These are NOT actual ATM locations or crime locations.
CITY_ZONES = [
    ("Punjab", "Ludhiana", 30.9010, 75.8573),
    ("Punjab", "Amritsar", 31.6340, 74.8723),
    ("Punjab", "Jalandhar", 31.3260, 75.5762),

    ("Haryana", "Gurugram", 28.4595, 77.0266),
    ("Haryana", "Faridabad", 28.4089, 77.3178),
    ("Haryana", "Hisar", 29.1492, 75.7217),

    ("Delhi", "North Delhi", 28.7041, 77.1025),
    ("Delhi", "South Delhi", 28.5245, 77.1855),
    ("Delhi", "East Delhi", 28.6280, 77.2950),

    ("Uttar Pradesh", "Lucknow", 26.8467, 80.9462),
    ("Uttar Pradesh", "Kanpur", 26.4499, 80.3319),
    ("Uttar Pradesh", "Varanasi", 25.3176, 82.9739),

    ("Rajasthan", "Jaipur", 26.9124, 75.7873),
    ("Rajasthan", "Jodhpur", 26.2389, 73.0243),
    ("Rajasthan", "Udaipur", 24.5854, 73.7125),

    ("Maharashtra", "Mumbai", 19.0760, 72.8777),
    ("Maharashtra", "Pune", 18.5204, 73.8567),
    ("Maharashtra", "Nagpur", 21.1458, 79.0882),

    ("Gujarat", "Ahmedabad", 23.0225, 72.5714),
    ("Gujarat", "Surat", 21.1702, 72.8311),
    ("Gujarat", "Vadodara", 22.3072, 73.1812),

    ("Karnataka", "Bengaluru", 12.9716, 77.5946),
    ("Karnataka", "Mysuru", 12.2958, 76.6394),
    ("Karnataka", "Mangaluru", 12.9141, 74.8560),

    ("Tamil Nadu", "Chennai", 13.0827, 80.2707),
    ("Tamil Nadu", "Coimbatore", 11.0168, 76.9558),
    ("Tamil Nadu", "Madurai", 9.9252, 78.1198),

    ("West Bengal", "Kolkata", 22.5726, 88.3639),
    ("West Bengal", "Siliguri", 26.7271, 88.3953),
    ("West Bengal", "Durgapur", 23.5204, 87.3119),
]

N_ZONES = len(CITY_ZONES)


def generate_dataset(
    output_path="data/raw/synthetic_atm_data.csv"
):
    rng = np.random.default_rng(SEED)

    dates = pd.date_range(
        START_DATE,
        periods=N_DAYS,
        freq="D"
    )

    # Generate fictional zone coordinates near each city anchor.
    # Small random offsets prevent all zones from overlapping.
    zone_metadata = []

    for i, (state, city, base_lat, base_lon) in enumerate(CITY_ZONES):
        zone_metadata.append({
            "zone_id": f"ZONE_{i + 1:03d}",
            "state": state,
            "city": city,
            "latitude": base_lat + rng.normal(0, 0.025),
            "longitude": base_lon + rng.normal(0, 0.025),
        })

    zone_activity = rng.uniform(0.75, 1.35, N_ZONES)
    zone_risk = rng.uniform(0.65, 1.55, N_ZONES)

    records = []

    for z, zone in enumerate(zone_metadata):

        for i, date in enumerate(dates):

            dow = date.dayofweek
            weekend = int(dow >= 5)
            month = date.month

            hour_peak = (
                1.0
                + 0.12 * (dow in [4, 5])
                + 0.08 * (month in [10, 11, 12])
            )

            withdrawal_count = int(
                rng.poisson(
                    75 * zone_activity[z] * hour_peak
                )
            )

            avg_withdrawal_amount = float(
                np.clip(
                    rng.normal(
                        2600 + 250 * zone_activity[z],
                        650
                    ),
                    500,
                    6500
                )
            )

            total_withdrawal_amount = (
                withdrawal_count * avg_withdrawal_amount
            )

            unusual_activity = int(
                rng.binomial(
                    max(withdrawal_count, 1),
                    min(0.025 * zone_risk[z], 0.12)
                )
            )

            seasonal = (
                1 + 0.18 * np.sin(2 * np.pi * i / 30.0)
            )

            weekend_factor = 1.12 if weekend else 1.0

            rate = (
                0.34 * zone_risk[z] * seasonal * weekend_factor
                + 0.012 * unusual_activity
                + 0.000002 * withdrawal_count
            )

            incident_count = int(
                rng.poisson(max(rate, 0.03))
            )

            records.append({
                "zone_id": zone["zone_id"],
                "state": zone["state"],
                "city": zone["city"],
                "date": date,
                "latitude": zone["latitude"],
                "longitude": zone["longitude"],
                "day_of_week": dow,
                "month": month,
                "is_weekend": weekend,
                "atm_count": int(rng.integers(3, 13)),
                "withdrawal_count": withdrawal_count,
                "avg_withdrawal_amount": round(
                    avg_withdrawal_amount, 2
                ),
                "total_withdrawal_amount": round(
                    total_withdrawal_amount, 2
                ),
                "unusual_activity_count": unusual_activity,
                "cashout_incident_count": incident_count,
            })

    daily = (
        pd.DataFrame(records)
        .sort_values(["zone_id", "date"])
        .reset_index(drop=True)
    )

    grouped = daily.groupby("zone_id", group_keys=False)

    # Historical rolling features: shift(1) prevents leakage.
    for window in [7, 30]:

        daily[f"withdrawals_sum_{window}d"] = (
            grouped["withdrawal_count"].transform(
                lambda s: s.shift(1).rolling(
                    window, min_periods=window
                ).sum()
            )
        )

        daily[f"unusual_activity_sum_{window}d"] = (
            grouped["unusual_activity_count"].transform(
                lambda s: s.shift(1).rolling(
                    window, min_periods=window
                ).sum()
            )
        )

        daily[f"incidents_sum_{window}d"] = (
            grouped["cashout_incident_count"].transform(
                lambda s: s.shift(1).rolling(
                    window, min_periods=window
                ).sum()
            )
        )

    # Target: incidents during the next 7 days (t+1 to t+7).
    daily["target_incidents_next_7d"] = (
        grouped["cashout_incident_count"].transform(
            lambda s: s.shift(-1)
            .rolling(7, min_periods=7)
            .sum()
            .shift(-6)
        )
    )

    daily["target_incidents_next_7d"] = (
        daily["target_incidents_next_7d"].astype(float)
    )

    daily["target_risk"] = pd.cut(
        daily["target_incidents_next_7d"],
        bins=[-0.1, 1, 3, np.inf],
        labels=["Low", "Medium", "High"]
    )

    # Remove rows without complete historical or future windows.
    daily = daily.dropna(
        subset=[
            "withdrawals_sum_30d",
            "unusual_activity_sum_30d",
            "incidents_sum_30d",
            "target_incidents_next_7d",
            "target_risk"
        ]
    ).copy()

    daily["target_incidents_next_7d"] = (
        daily["target_incidents_next_7d"].astype(int)
    )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    daily.to_csv(output, index=False)

    print(f"Saved {len(daily):,} rows to {output}")
    print(f"\nNumber of simulated zones: {N_ZONES}")
    print(f"Number of states: {daily['state'].nunique()}")

    print("\nZones per state:")
    print(
        daily[["state", "zone_id"]]
        .drop_duplicates()
        .groupby("state")
        .size()
    )

    print("\nRisk label distribution:")
    print(daily["target_risk"].value_counts())

    print(
        "\nDate range:",
        daily["date"].min(),
        "to",
        daily["date"].max()
    )

    return daily


if __name__ == "__main__":
    generate_dataset()
