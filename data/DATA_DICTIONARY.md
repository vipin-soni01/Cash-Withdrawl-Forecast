# Phase 1 Data Dictionary

| Column | Meaning |
|---|---|
| zone_id | Synthetic geographical zone identifier |
| date | Observation date |
| latitude, longitude | Fictional zone-centroid coordinates |
| day_of_week, month, is_weekend | Calendar features |
| atm_count | Simulated number of ATMs in zone |
| withdrawal_count | Aggregate daily withdrawal count |
| avg_withdrawal_amount | Simulated average amount per withdrawal |
| total_withdrawal_amount | Aggregate daily withdrawal amount |
| unusual_activity_count | Simulated aggregate unusual-activity count |
| cashout_incident_count | Simulated incident count on the observation date |
| withdrawals_sum_7d / 30d | Previous 7/30-day aggregate withdrawals |
| unusual_activity_sum_7d / 30d | Previous 7/30-day unusual activity |
| incidents_sum_7d / 30d | Previous 7/30-day incident counts |
| target_incidents_next_7d | Target: incidents during next 7 days |
| target_risk | Target class derived from next-7-day count |

**Leakage warning:** `cashout_incident_count` is the current-day outcome and should not be used as a predictor for a forecast made at the start of that date. The supplied preprocessing feature list excludes it. Target columns must always be excluded from X.
