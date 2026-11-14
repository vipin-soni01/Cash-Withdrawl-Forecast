"""
Phase 1 preprocessing utilities.
Fit imputers/encoders/scalers on training data only in Phase 2.
"""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_CLASS = "target_risk"
TARGET_COUNT = "target_incidents_next_7d"

# Do not include target columns or same-day outcome columns in model features.
NUMERIC_FEATURES = [
    "latitude", "longitude", "day_of_week", "month", "is_weekend",
    "atm_count", "withdrawal_count", "avg_withdrawal_amount",
    "total_withdrawal_amount", "unusual_activity_count",
    "withdrawals_sum_7d", "unusual_activity_sum_7d", "incidents_sum_7d",
    "withdrawals_sum_30d", "unusual_activity_sum_30d", "incidents_sum_30d",
]
CATEGORICAL_FEATURES = ["zone_id"]

def build_preprocessor():
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
    ])

def split_features_target(df, target=TARGET_CLASS):
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y = df[target].copy()
    return X, y
