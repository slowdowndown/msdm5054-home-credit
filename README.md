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
├── CONTRIBUTING.md            # Workflow and commit conventions
├── .gitignore
├── docs/
│   ├── division-of-labor.md   # Division of labor
│   ├── a/                     # SHU Yi: V0 data entry and handoff
│   ├── eda/                   # CAO Yixin: EDA and feature handoff
│   └── report/                # Final report (poster or NIPS-style PDF)
├── data/                      # Data (not tracked)
│   ├── raw/                   # Raw Kaggle data
│   └── processed/             # Processed data (V0/V1/V2)
├── notebooks/                 # Exploratory notebooks (.ipynb)
├── scripts/
│   └── eda/                   # CAO Yixin: EDA and feature scripts
├── src/                       # Shared Python modules (.py)
└── results/
    ├── a/                     # SHU Yi: V0 acceptance snapshot
    └── eda/                   # CAO Yixin: EDA results and figures
```

## Code organization

Code is organized by artifact type, not by owner:

- notebooks/ — exploratory analysis and experiments (.ipynb), named by topic.
- src/ — reusable or shared code as importable .py modules: data loading, preprocessing, feature functions, metrics, training scripts.

## Conventions

- data/ is not tracked (see .gitignore).
- Field definitions, missing-value handling, encoding, split, and metrics are agreed in docs/division-of-labor.md (Phase 2).
- Development workflow: see CONTRIBUTING.md.


## V0 data pipeline and baseline

The A-part V0 workflow has been validated locally end to end. Start with [the notebook](notebooks/A_data_and_baseline.ipynb) and [the run and handoff guide](docs/a/使用与交接说明.md). Shared loading, splitting and preprocessing are in `src/data_pipeline.py`; `src/baseline.py` builds the baseline pipeline.

### Run V0

1. Use a separate Python 3.12 environment and install `python -m pip install -r docs/a/requirements-a.txt`. Register/select that environment as the Jupyter kernel as described in the handoff guide. The complete tested macOS ARM64 environment is recorded in `docs/a/requirements-lock.txt`; other platforms should use the main dependency list.
2. Download the official Kaggle files into `data/raw/`: `application_train.csv`, `application_test.csv`, `HomeCredit_columns_description.csv` and `sample_submission.csv`. Keep raw files unchanged and outside Git.
3. Open `notebooks/A_data_and_baseline.ipynb` from the repository root or `notebooks/`, restart the kernel and run all cells. The workflow checks input fingerprints, builds the fixed split, trains and evaluates the baseline, and exports test predictions.
4. Generated models, splits and record-level validation predictions stay in ignored `data/processed/v0/`. The candidate CSV is `results/submissions/submission_v0.csv`; an existing candidate is not overwritten. Check it with `python src/validate_submission.py results/submissions/submission_v0.csv`. This does not submit to Kaggle.

### Proposed V0 comparison protocol — pending team confirmation

These settings are implemented in the current handoff; SHU Yi and the modeling, feature and evaluation owners should confirm them before using them as the shared comparison standard.

- **Data and alignment:** application main tables only. Align all features and predictions by `SK_ID_CURR`; exclude this ID and `TARGET` from model inputs. Input fingerprints are recorded in `docs/a/data_manifest_v0.json`.
- **Split:** stratify by `TARGET`, seed **42**, **80% training / 20% validation** (246,008 / 61,503 rows). Reuse the customer assignments generated from `docs/a/split_protocol.json`; do not independently resplit and compare scores directly.
- **Preprocessing:** treat `DAYS_EMPLOYED=365243` as missing; apply `log1p` to income, credit, annuity and goods-price amounts, with negative values treated as missing. Drop columns with more than 80% missing values using training data only. Use median imputation, missing indicators and scaling for numeric fields; `Missing` imputation and one-hot encoding for categories, allowing unseen categories. Learned preprocessing is fitted only on training data, including within each future CV fold.
- **Evaluation:** use holdout ROC AUC as the primary metric and Average Precision as a supplementary metric. The current holdout is not cross-validation. Any V1/V2 comparison should record changes and use the agreed validation setup.
- **Ownership:** SHU Yi maintains the data entry point, split and end-to-end checks; ZHANG Yajing owns modeling/CV/tuning. The shared baseline is a starting point, not a reassignment of modeling responsibilities.

### Validated results and limits

Local validation: **ROC AUC 0.751239**, **Average Precision 0.237504**. The fixed customer split and reported metrics match the previous baseline. See [acceptance record](results/a/acceptance.json), [metrics](results/a/metrics.csv) and [figures](results/a/figures/); earlier aggregate snapshots are under `results/a/history/pre_refactor/`.

A **48,744-row** candidate CSV was generated and passed ID, column and probability checks. It is a local output, not an uploaded repository artifact; there is **no Kaggle submission or platform score yet**. The candidate uses the model fitted on the 80% training subset. Final model selection and any full-data refit should be coordinated with the modeling owner.

The saved V0 model now includes cleaning: add `src/` to the Python module path and pass raw application rows to `predict_proba`; do not clean them twice. All notebook code cells completed successfully. A sandbox warning occurred during kernel shutdown cleanup after computation; saved-model predictions and output files were independently checked.

## EDA and feature handoff

CAO Yixin's EDA phase (steps 1–8) is complete. Per-column keep/drop/transform decisions for V1 are in [docs/eda/column_decisions.md](docs/eda/column_decisions.md), with the machine-readable list in `results/eda/column_decisions.csv`. Full findings are in [docs/eda/eda_findings.md](docs/eda/eda_findings.md); figures 00–27 are in `results/eda/figures/`. See the [handoff guide](docs/eda/使用与交接说明.md) for reproduction and the relationship to the V0 protocol. Statistics use the 80% train fold of the fixed split only.
