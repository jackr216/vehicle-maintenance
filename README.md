# Vehicle Maintenance Prediction

A predictive maintenance project to help the business move from reactive to proactive vehicle servicing.

## Objectives

- **When** will a vehicle next need a repair? *(Survival Analysis)*
- **Which** vehicles are at highest risk of breakdown? *(Risk Classification)*
- **What** maintenance should be scheduled and when? *(Combined Output)*

## Data Sources

- `data/raw/` — place raw data files here before running any notebooks
  - Repair history (repair category, date, cost, vehicle ID)
  - Vehicle info (mileage, age, make/model etc.)
  - Driver scores (overall score per driver, linked to vehicle)

## Project Structure

```
vehicle_maintenance/
├── data/
│   ├── raw/            # Original data files — do not modify
│   └── processed/      # Cleaned and engineered features
├── notebooks/          # Jupyter notebooks (numbered in order)
├── src/                # Reusable Python scripts/modules
├── outputs/
│   ├── models/         # Saved model files
│   └── reports/        # Final outputs and maintenance schedules
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Modelling Approach

1. **Survival Analysis** — uses `lifelines` to model time between repairs per category (tyres, brakes, engine etc.)
2. **Risk Classifier** — XGBoost model outputting High/Medium/Low risk per vehicle
3. **Maintenance Schedule** — combined output merging both models into an actionable report

## Notes

- Driver score is assigned based on the current driver linked to the vehicle at time of model run
- Further development: incorporate driver change history timeline for more accurate historical attribution
