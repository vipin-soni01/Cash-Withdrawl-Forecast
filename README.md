# Cybercrime Cash-Withdrawal Location Forecast

**Supervised Machine Learning-Based Seven-Day Risk Forecasting**  
*B.Tech Computer Science and Engineering (AI & ML) — Lovely Professional University*  
*Author: Vipin Soni*

---

## ⚠️ Important Synthetic-Data & Scope Disclaimer

All transaction activity, withdrawal amounts, unusual activity signals, incident counts, risk labels, and geographical coordinates in this repository are **100% synthetic and simulated** (`src/data_generator.py`).
- Coordinates are random Gaussian offsets around approximate city centers and **do not** represent real ATM kiosks, bank branches, or actual crime hotspots.
- Predictions and class probabilities are statistical estimates from an academic prototype and **must not** be used for real-world law-enforcement, banking security, or punitive decisions.

---

## 1. Project Overview & Objectives

Suspicious cash-withdrawal activity often exhibits localized spatial-temporal clustering over multi-day windows. Traditional reactive monitoring flags anomalies only after spikes occur on the observation day. This academic project formulates a **seven-day forward risk forecasting framework** on a simulated zone-day dataset.

### Core Objectives
1. **Synthetic Zone-Day Data Generation:** Simulate 540 days of daily ATM withdrawal activity, unusual signal counts, and incident counts across **30 fictional zones** spanning **10 Indian states** (`15,090` complete model-ready records).
2. **Exploratory Data Analysis (EDA):** Analyze temporal patterns, seasonal cycles, weekend multipliers, and zone-level risk distributions (`notebooks/01_data_exploration.ipynb`).
3. **Leak-Free Feature Engineering & Temporal Splitting:** Engineer rolling 7-day and 30-day statistics, per-ATM ratios, and cyclical seasonal features (`23` predictors total), and partition data chronologically with a **7-day embargo gap** (`notebooks/02_preprocessing.ipynb`).
4. **Multi-Algorithm Comparison & Tuning:** Train and compare **6 supervised classifiers** (Logistic Regression, Random Forest, Support Vector Machine, K-Nearest Neighbors, Decision Tree, and Gradient Boosting) and tune top pipelines using **5-fold time-aware cross-validation** (`notebooks/03_classification.ipynb`, `notebooks/03_hyperparameter_optimization.ipynb`, `notebooks/05_advanced_model_improvement.ipynb`).
5. **Explainable AI (SHAP & LIME):** Quantify global feature importance via **SHAP** and explain individual zone-day forecasts via **LIME** (`notebooks/04_explainable_ai.ipynb`).
6. **Interactive Streamlit Dashboard:** Provide a 4-module web interface (`app/app.py`) for India-wide simulated map visualization, historical zone trend drill-downs, single-zone risk inference, batch CSV prediction, and model transparency.

---

## 2. Dataset Description

- **File:** `data/raw/synthetic_atm_data.csv` (see `data/DATA_DICTIONARY.md`)
- **Model-Ready Observations:** `15,090` zone-day rows (`503` effective days × `30` zones after removing incomplete 30-day historical lookback and 7-day forward target windows)
- **Date Coverage:** `2025-01-31` to `2026-06-17`
- **Geographic Coverage:** `30` fictional zones (`ZONE_001` to `ZONE_030`) across `10` states (`3` cities per state: Punjab, Haryana, Delhi, Uttar Pradesh, Rajasthan, Maharashtra, Gujarat, Karnataka, Tamil Nadu, West Bengal)

### Target Variable Definition (`target_risk`)
Derived from `target_incidents_next_7d` (cumulative simulated incidents from day $t+1$ to $t+7$):
- **Low Risk:** `0 – 1` incidents in next 7 days (`3,408` rows / `22.58%`)
- **Medium Risk:** `2 – 3` incidents in next 7 days (`6,257` rows / `41.46%`)
- **High Risk:** `4+` incidents in next 7 days (`5,425` rows / `35.95%`)

### Model Input Features (`23` Predictors)
- **Categorical (`1`):** `zone_id` (One-Hot Encoded)
- **Base Numerical (`16`):** `latitude`, `longitude`, `day_of_week`, `month`, `is_weekend`, `atm_count`, `withdrawal_count`, `avg_withdrawal_amount`, `total_withdrawal_amount`, `unusual_activity_count`, `withdrawals_sum_7d`, `unusual_activity_sum_7d`, `incidents_sum_7d`, `withdrawals_sum_30d`, `unusual_activity_sum_30d`, `incidents_sum_30d`
- **Engineered Numerical (`6`):**
  - `withdrawals_per_atm = withdrawal_count / atm_count`
  - `unusual_activity_ratio = unusual_activity_count / withdrawal_count`
  - `avg_daily_incidents_30d = incidents_sum_30d / 30`
  - `withdrawal_amount_per_atm = total_withdrawal_amount / atm_count`
  - `season_30d_sin = sin(2π · day_index / 30)`
  - `season_30d_cos = cos(2π · day_index / 30)`

*(Note: `cashout_incident_count` on day $t$ and future target columns are strictly excluded from predictors to prevent target leakage).*

---

## 3. Temporal Splitting & Model Evaluation Results

### Chronological Split with 7-Day Embargo
- **Training Set:** `2025-01-31` to `2026-03-01` (`11,850` rows)
- **7-Day Embargo Gap:** `2026-03-02` to `2026-03-08` (`210` rows omitted so 7-day forward training targets do not overlap with the test period)
- **Held-Out Test Set:** `2026-03-09` to `2026-06-17` (`3,030` rows)

### 5-Fold Time-Aware Cross-Validation (`results/phase4_cv_comparison.csv`)
| Model Pipeline | Best CV Macro F1 | Optimal Hyperparameters |
| :--- | :---: | :--- |
| **Logistic Regression (Selected)** | **44.35%** (`0.4435`) | `C=1, class_weight=None` |
| Random Forest | 43.83% (`0.4383`) | `n_estimators=150, max_depth=10, min_samples_leaf=2, max_features='sqrt', class_weight='balanced'` |
| Support Vector Machine (SVM) | 43.40% (`0.4340`) | `C=1, gamma=0.01, kernel='rbf', class_weight='balanced'` |

### Held-Out Test Set Benchmark (`results/phase4_test_metrics.csv`, $N = 3,030$)
| Model | Accuracy | Balanced Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | ROC-AUC (OVR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Selected)** | **46.96%** | **42.23%** | **43.46%** | **42.23%** | **42.05%** | **45.69%** | **59.98%** |
| Random Forest | 40.40% | 42.21% | 39.92% | 42.21% | 39.51% | 39.48% | 59.98% |
| Support Vector Machine (SVM) | 39.57% | 42.04% | 40.10% | 42.04% | 39.15% | 39.16% | 60.08% |
| Majority-Class Baseline | 45.25% | 33.33% | 15.08% | 33.33% | 20.77% | 28.19% | 50.00% |

**Interpretation:** Tuned Logistic Regression more than doubles the Majority-Class Baseline Macro F1 (`42.05%` vs `20.77%`) and identifies `52.84%` of High-Risk test instances (`548 / 1,037`). Overall predictive separation remains modest (`46.96%` accuracy, `59.98%` ROC-AUC) due to the stochastic Poisson/Binomial noise in the synthetic generator.

---

## 4. Repository Structure

```text
Cybercrime-Cash-Withdrawal-Forecast/
├── app/
│   ├── app.py                              # Interactive 4-module Streamlit dashboard
│   └── alert_sound.b64                     # Synthesized audio asset for simulation toggle
├── data/
│   ├── DATA_DICTIONARY.md                  # Schema & leakage notes
│   ├── raw/synthetic_atm_data.csv          # 15,090 zone-day synthetic dataset
│   └── processed/batch_prediction_sample.csv # Sample processed dataset for batch testing
├── models/
│   ├── best_risk_classifier.joblib         # Selected production pipeline bundle (Logistic Regression)
│   └── *.joblib                            # Saved Phase 3 comparison models (RF, SVM, KNN, DT, GB)
├── notebooks/
│   ├── 01_data_exploration.ipynb           # EDA & visualizations
│   ├── 02_preprocessing.ipynb              # Feature engineering & chronological split
│   ├── 03_classification.ipynb             # 6-model supervised learning comparison
│   ├── 03_hyperparameter_optimization.ipynb# 5-fold time-aware CV & hyperparameter tuning
│   ├── 04_explainable_ai.ipynb             # Global SHAP & local LIME explainability
│   └── 05_advanced_model_improvement.ipynb # Class-weighted & ensemble experiments
├── results/
│   ├── phase4_test_metrics.csv             # Held-out test evaluation metrics
│   ├── phase4_best_model_confusion_matrix.csv
│   ├── phase4_best_model_classification_report.csv
│   ├── phase4_cv_comparison.csv
│   ├── shap_high_risk_importance.png       # Global SHAP feature importance plot
│   └── lime_high_risk_explanation.png      # Local LIME instance explanation plot
├── src/
│   ├── data_generator.py                   # Reproducible synthetic dataset generator
│   └── preprocessing.py                    # Scikit-Learn ColumnTransformer utilities
├── requirements.txt
└── README.md
```

---

## 5. Setup, Training & Launch Instructions

### 1. Create Virtual Environment & Install Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Regenerate Synthetic Dataset (Optional)
```powershell
python src/data_generator.py
```

### 3. Launch the Streamlit Application
```powershell
streamlit run app/app.py
```
The dashboard will open at `http://localhost:8501` with four modules:
1. **📊 Dashboard Overview:** 30-zone interactive India map (`px.scatter_map`), State/City/Risk filters, KPI cards, state-wise risk distributions, and historical zone trend drill-down.
2. **🔍 Single Zone Risk Prediction:** Interactive 23-feature prediction form, 1-click presets, live local feature contribution breakdown, and simulated cashout attack stress-test toggle.
3. **📁 Batch CSV Prediction:** Upload raw or processed CSV files with automatic derived-feature computation, validation, and downloadable CSV predictions.
4. **ℹ️ Model Intelligence & Explainability:** Held-out test metrics, confusion matrix, classification report, CV benchmarks, and SHAP/LIME visual explanations.

---

## 6. Limitations & Future Scope

### Limitations
- **Synthetic Data & Fictional Coordinates:** All data points and map coordinates are mathematically simulated and unvalidated against real crime records.
- **Modest Predictive Separation:** High stochastic overlap across Poisson-generated classes limits overall accuracy (`46.96%`).
- **Academic Prototype:** Not intended for operational banking security or law-enforcement deployment.

### Future Scope
- Evaluation on anonymized, privacy-protected empirical financial datasets.
- Spatio-temporal deep learning (Temporal Fusion Transformers, LSTMs, Graph Neural Networks).
- Real-time streaming feature pipelines and post-hoc probability calibration.
