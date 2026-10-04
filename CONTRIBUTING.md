# Contributing

## Workflow

- Work directly on main. The timeline is short, so skip feature branches.
- Pull before starting work and again before pushing. Never force-push.
- Edit only the files you own. Sync before editing shared files (README.md, docs/).

## Commit messages

Prefix commits by area:

| Prefix | Area |
| --- | --- |
| data: | data loading, preprocessing, versioning |
| feat: | feature engineering |
| model: | training, cross-validation, tuning |
| eval: | metrics, plots, SHAP |
| docs: | documentation |
| report: | report content |

## Data and secrets

- Kaggle data stays in data/ (gitignored) and is not committed; share it outside git if needed.
- Never commit credentials (kaggle.json) or large data files.
