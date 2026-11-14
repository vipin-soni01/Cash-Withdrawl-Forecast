<<<<<<< HEAD
# Cybercrime Cash-Withdrawal Location Forecast

An advanced supervised-learning academic project using a **synthetic** zone-day dataset.

## Important scope note
All transaction activity, incident counts, risk labels, and coordinates are simulated.
The project demonstrates forecasting methodology; it does not identify real criminals,
real ATM users, or actual crime hotspots.

## Phase 1 setup

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python src/data_generator.py
```

Open `notebooks/01_data_exploration.ipynb` in Jupyter.

## Dataset design
Each row represents one geographical zone on one date. Features include aggregate ATM
activity and historical rolling statistics. Targets are:
- `target_incidents_next_7d`: number of simulated incidents in the next seven days.
- `target_risk`: Low (0–1), Medium (2–3), High (4+).

The model must not use target columns or future information as predictors. Later phases
will use chronological evaluation and fit preprocessing only on training data.
=======
# Cash-Withdrawl-Forecasr
>>>>>>> origin/main
