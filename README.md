# Home Credit Default Risk

Team repository for MSDM5054 Statistical Machine Learning — Mini-Project 1. Topic: Kaggle [Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk/).

## Overview

Home Credit serves people with insufficient or absent credit histories by using alternative data (telco, transactional, and other information) to predict clients' repayment ability. The task is binary classification: TARGET = 1 indicates default, TARGET = 0 indicates on-time repayment. The evaluation metric is ROC AUC. The data consists of 7 tables; the main table is application_train.

## Roles

| Member | Responsibility |
| --- | --- |
| SHU Yi | Data pipeline + baseline collaboration + Kaggle |
| CAO Yixin | EDA + feature engineering |
| ZHANG Yajing | Modeling + cross-validation + tuning |
| SU Zhiyu | Evaluation + SHAP/error analysis + report |

See docs/division-of-labor.md for the full division of labor.

## Repository structure

```text
msdm5054-home-credit/
├── README.md                  # Overview and usage
├── requirements.txt           # Dependencies
├── .gitignore
├── docs/
│   ├── division-of-labor.md   # Division of labor
│   └── report/                # Final report (poster or NIPS-style PDF)
├── data/                      # Data (not tracked)
│   ├── raw/                   # Raw Kaggle data
│   └── processed/             # Processed data (V0/V1/V2)
├── notebooks/                 # Exploratory notebooks (.ipynb)
├── src/                       # Reusable Python modules (.py)
└── results/                   # Submissions and figures
```

## Code organization

Code is organized by artifact type, not by owner:

- notebooks/ — exploratory analysis and experiments (.ipynb), named by topic.
- src/ — reusable or shared code as importable .py modules: data loading, preprocessing, feature functions, metrics, training scripts.

## Conventions

- data/ is not tracked (see .gitignore).
- Field definitions, missing-value handling, encoding, split, and metrics are agreed in docs/division-of-labor.md (Phase 2).
- Development workflow: see CONTRIBUTING.md.
