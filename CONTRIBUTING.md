# Contributing

## Development

- The team currently shares `main`. Coordinate changes to shared modules and documentation before editing.
- Run commands from the repository root in a dedicated Python environment.
- Run `python -m unittest discover -s tests -v` after changes to shared modules.
- Recompute evaluation after changing prediction inputs and review metric differences.
- Review the Git diff before committing. Keep report edits separate from structure changes.
- Run `git pull --rebase origin main` before pushing. Resolve conflicts without force-pushing shared history.

## Artifacts

| Location | Convention |
| --- | --- |
| `docs/report/report.pdf` | Authoritative final submission |
| `docs/report/report.tex` | Editable source; maintain valid figure paths |
| `docs/report/archive/` | Historical drafts |
| `docs/data/` | Data fingerprints, split and preprocessing protocol |
| `results/` | Experimental evidence, fitted estimators and submission predictions |
| `data/` | Local raw data, split assignments and generated baseline models; ignored |
| `requirements/locks/` | Original environment records with platform context |

- Organize files by function and artifact type. Record team responsibilities in README.
- Preserve IDs, labels and probability precision in prediction files.
- Preserve experimental source commits and hashes in provenance records when migrating paths.
- Keep Kaggle credentials, raw data, virtual environments and LaTeX caches outside Git.
- Saved V1 estimators require transformed inputs. Changes to preprocessing are separate functional work.

## Commit messages

| Prefix | Scope |
| --- | --- |
| `data:` | Data loading, preprocessing and split protocols |
| `feat:` | Feature engineering |
| `model:` | Training, cross-validation and tuning |
| `eval:` | Evaluation metrics, alignment and figures |
| `docs:` | Documentation |
| `report:` | Final report revisions |
| `refactor:` | Structure changes without intended model behavior changes |

## Reproduce evaluation without raw data

Run commands from the repository root. Evaluation uses committed prediction files and modeling artifacts without fitting models or accessing Kaggle.

```bash
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` on macOS/Linux. Then run:

```bash
python -m pip install -r requirements/evaluation.txt
python -m unittest discover -s tests -v
python src/evaluation.py --root .
```

Evaluation recomputes both models' metrics, aligns predictions by `SK_ID_CURR`, runs a 500-replicate bootstrap, and writes tables, provenance and figures under `results/evaluation/`. Existing evaluation outputs are overwritten. For interactive inspection, use [03_evaluation.ipynb](notebooks/03_evaluation.ipynb).

## Reproduce data preparation and modeling

1. Use Python 3.12 for the recorded baseline environment and install `python -m pip install -r requirements.txt`.
2. Place the official `application_train.csv`, `application_test.csv`, `HomeCredit_columns_description.csv` and `sample_submission.csv` in `data/raw/`. Raw data and credentials are excluded from Git. The project uses the application tables; auxiliary-table aggregation is not implemented.
3. Run `python src/reproduce_split.py`. Data fingerprints and the split protocol are in [docs/data/](docs/data/). An existing split is checked rather than replaced.
4. Open [01_data_and_baseline.ipynb](notebooks/01_data_and_baseline.ipynb) for V0. The EDA execution order is recorded in [the EDA guide](docs/eda/使用与交接说明.md). Committed feature decisions can be used without rerunning EDA.
5. Open [02_modeling.ipynb](notebooks/02_modeling.ipynb), restart the kernel and run all cells to reproduce the model comparisons, CV, full-data fitting and predictions.
6. Recompute evaluation and validate the selected submission:

```bash
python src/evaluation.py --root .
python src/validate_submission.py results/submissions/submission_v2_xgboost.csv
```

Submission validation requires the official sample and test files and does not upload to Kaggle. Notebooks refuse to overwrite existing submission CSVs. Before rerunning, preserve existing submissions outside their expected output filenames. Other modeling exports overwrite artifacts; use a separate checkout for new experiments.

The committed `*_preprocessed_input.joblib` estimators require the exact transformed 83-column matrix. They do not accept raw application rows. V1 preprocessing remains in the modeling notebook; a standalone fitted V1 preprocessing pipeline is not exported. Environment locks in `requirements/locks/` record the original runs and are not universal installation files.

## Build the report

The submitted PDF is committed. To rebuild it, install a LaTeX distribution with `latexmk` and the packages used by the source. Run from `docs/report/`:

```bash
latexmk -pdf report.tex
```

Figures are referenced from `results/eda/figures/` and `results/evaluation/figures/`. LaTeX build caches are ignored. Recomputing experiments does not automatically update report text or the submitted PDF.

## Team and execution entry points

| Member | Responsibility | Main directories | Execution entry point |
| --- | --- | --- | --- |
| SHU Yi | Data entry, fixed split, V0 baseline and submission checks | `docs/data/`, `results/baseline/` | `01_data_and_baseline.ipynb`, `src/reproduce_split.py` |
| CAO Yixin | EDA, feature decisions, figures, Kaggle submission and report conversion | `docs/eda/`, `scripts/eda/`, `results/eda/` | EDA guide and scripts |
| ZHANG Yajing | LightGBM/XGBoost, CV, tuning, selection and full-data fitting | `docs/modeling/`, `results/modeling/` | `02_modeling.ipynb` |
| SU Zhiyu | Recomputed evaluation, aligned comparisons, error analysis and integrated report | `docs/evaluation/`, `results/evaluation/` | `03_evaluation.ipynb`, `src/evaluation.py` |

## Historical records

The former `a/c/d` directories correspond to data/baseline, modeling and evaluation. Existing handoff guides remain available under the renamed directories; historical status statements are marked as such.

Acceptance and provenance records retain the original experimental source hashes. Their migrated path keys identify the corresponding files; the recorded hashes describe the original run rather than the current refactored source.
