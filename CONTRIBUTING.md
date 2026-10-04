# Contributing

## Workflow

- Work directly on main. The timeline is short, so skip feature branches.
- Edit only the files you own. Sync before editing shared files (README.md, docs/).

### Pull before every push (important)

All four members push to the same main branch. If someone else pushed after your last pull, your push is rejected. Run this before every push:

```bash
git pull --rebase origin main
```

If a push is still rejected, do not force-push. Pull again, resolve the conflict, then push. Never use `--force`.

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
