# CLAUDE.md — Vehicle Maintenance Prediction

## Project Overview

Predictive maintenance project for a commercial van fleet (~715 active vehicles across ~45 branches). The goal is to move from reactive to proactive vehicle servicing by predicting which vehicles need maintenance, when, and what type.

## Key Questions the Project Answers

1. **When** will a vehicle next need a repair? → Survival Analysis
2. **Which** vehicles are highest risk? → XGBoost Risk Classifier (High / Medium / Low)
3. **What** should be scheduled? → Combined maintenance schedule output

## Repository Structure

```
vehicle_maintenance/
├── data/
│   ├── raw/                # Original Excel files — do not modify
│   ├── raw_anon/           # Anonymised version of raw data (used in notebooks)
│   └── processed/          # Cleaned CSVs output by notebooks 02–05
├── notebooks/              # Numbered Jupyter notebooks (run in order)
├── src/                    # Reusable Python modules (if any)
├── outputs/
│   ├── models/             # Saved model files (XGBoost pickle etc.)
│   └── reports/            # Final Excel workbook + chart PNGs
├── requirements.txt
├── README.md
└── .gitignore
```

## Data Sources (5 raw files)

| File | Contents |
|---|---|
| `Vehicle_Info.xlsx` | Registration, make, model, asset type, status |
| `Vehicle_Driver.xlsx` | Current driver assignment, MOT dates |
| `Vehicle_Mileage.xlsx` | Monthly mileage readings per vehicle |
| `Maintenance_Records.xlsx` | Repair history — category, date, cost, vehicle ID |
| `Driver_Scores.xlsx` | Weekly driver behaviour scores (acceleration, braking, speeding, cornering) |

## Notebook Pipeline (run sequentially)

| # | Notebook | Purpose |
|---|---|---|
| 01 | Data Exploration | Profile all five datasets, identify quality issues, document decisions |
| 02 | Data Cleaning | Filter to vans only, clean dates, handle missing values, join datasets → `data/processed/` |
| 03 | Feature Engineering | Build per-vehicle features: repair history, mileage, driver scores, MOT status, category breakdowns → `features.csv`, `features_active.csv` |
| 04 | Survival Analysis & Rule-Based Flags | Kaplan-Meier + Weibull AFT for Engine/Electrical/Cooling; rule-based flags for Brakes/Tyres → `survival_predictions.csv` |
| 05 | Risk Classification | XGBoost classifier producing High/Medium/Low risk per vehicle → `risk_scores.csv` |
| 06 | Maintenance Schedule Output | Merges all outputs into a single business-facing Excel workbook with Summary, Schedule, High Risk Detail, and Branch Summary sheets |

## Key Modelling Decisions

- **Vans only**: filtered to Medium Van, Small Van, Large Van asset types.
- **Driver scores**: only from May 2023 onward (pre-2023-05 values were a system default of 100).
- **Branch source of truth**: `Driver_Scores` table, not `Vehicle_Info` (outdated names in the latter).
- **2026 maintenance records excluded**: submission lag makes them unreliable at time of analysis.
- **Environmental Disposal records excluded**: not mechanical repairs.
- **Brakes & Tyres use rule-based flags** (not survival model) because of insufficient repeat data and a dealer warranty gap (~3 years) that distorts first-repair durations. Flag logic: vehicle age > 3 years AND no recorded repair in last 24 months.
- **Survival analysis** (Engine, Electrical, Cooling): Kaplan-Meier + Weibull AFT, 90-day prediction horizon.
- **Risk labelling is semi-supervised**: composite score created from survival probabilities + rule flags + supporting features, then bucketed into High/Medium/Low. XGBoost learns to generalise this scoring — not predicting an independent ground truth.
- **Missing driver assignments**: filled with fleet-average driver score.

## Key Output

`outputs/reports/Fleet_Maintenance_Schedule.xlsx` — 4 sheets:
1. **Summary** — fleet overview, risk breakdown, generated date, scoring methodology
2. **Maintenance Schedule** — one row per active vehicle sorted by risk, with flags, MOT status, and plain-English recommended action
3. **High Risk Detail** — filtered to High risk vehicles only
4. **Branch Summary** — per-branch risk breakdown sorted by % High Risk

## Tech Stack

- Python 3.14, Jupyter notebooks
- pandas, numpy, matplotlib, seaborn
- lifelines (survival analysis)
- xgboost, scikit-learn
- openpyxl (Excel output formatting)

## Known Limitations & Future Work

- Dealer warranty repairs (first ~3 years of vehicle life) are not captured in the data.
- Driver score is based on current driver assignment — no history of driver changes.
- Mileage is monthly readings, not true odometer snapshots.
- Future: automate monthly refresh pipeline, MOT failure prediction, cost forecasting, expand brakes/tyres to survival model as data grows.
