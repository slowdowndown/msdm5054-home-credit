# Home Credit Default Risk — Team Discussion Draft

Team: SHU Yi (data pipeline and Kaggle), CAO Yixin (EDA and features), ZHANG Yajing (modeling), SU Zhiyu (evaluation and report).

## Division of labor

Four roles that run in parallel with few dependencies between them. Within each role we separate what can start right away from what has to wait until the data is unified. Everyone gets their own part running first, then we merge; nobody waits for all the tables to be joined before starting.

### Phase 1: everyone starts immediately

| Who | Start now | Hand in |
| --- | --- | --- |
| SHU Yi | Read the competition description, download the data, and work out what each table means. Check the TARGET distribution, sample size, variable types, and missing values. Set up the shared directory and a notebook entry point. | A minimal usable dataset from the main table only, with simple preprocessing, so the baseline has data to run on. |
| CAO Yixin | Go through the application_train main table. List field types, missing rates, and meanings. Break the analysis down by income, loan, age, employment length, family, property/vehicle, and external scores. | A field overview and about ten interpretable feature ideas, for example loan amount / income, annuity / income, loan amount / annuity. |
| ZHANG Yajing | Take the raw main table, do simple imputation and categorical encoding, and build a Logistic Regression or LightGBM baseline. Get training, validation, prediction, and AUC working, and set up cross-validation. | A runnable model pipeline. The goal here is to get it running, not to chase the score. |
| SU Zhiyu | Set up the report folder and a results log. Write the background, the research questions, and notes on the data and metrics. Prepare reusable code for ROC, AUC, and the confusion matrix, and write down why accuracy alone is not enough. | A report skeleton, a results-table template, and reusable plotting functions. |

To avoid double work, SHU Yi owns the data entry and the end-to-end check, ZHANG Yajing owns the baseline model, and the two share one baseline pipeline.

### Phase 2: V0 as baseline, V1 to check improvements, V2 if time allows

Before we merge anything, we agree on one shared setup: the main data and field definitions, missing-value handling, categorical encoding, the train/validation split, and the metric. SHU Yi keeps the single entry point; everyone else plugs into the same version for any real comparison.

| Who | Phase 2 work and hand-in |
| --- | --- |
| SHU Yi | Build the main table, unify preprocessing and the train/validation split, and keep track of data versions, progress, and the Kaggle submission flow. |
| CAO Yixin | Finish the ratio and statistical features and do feature selection. Aggregate other tables if there is room. Hand in the feature table and a note on each feature. |
| ZHANG Yajing | Take CAO Yixin's features and run LightGBM/XGBoost with cross-validation and light tuning. Hand in the model code and the final model. |
| SU Zhiyu | Compare the models, look at the errors, and pull together figures and conclusions. Add SHAP if there is time. Hand in the evaluation results and the merged report. |

What each version means:

- V0 (minimal): main table plus simple processing only. It needs to be able to train, compute AUC, and produce a submission. Keep one complete runnable pipeline as the baseline to compare against later.
- V1 (basic features): add simple ratio features and basic statistics. Under the shared validation setup, check whether the features actually lift AUC, and write down the result and why.
- V2 (enhanced, optional): if we have time, multi-table aggregation, more complex features, model tuning, SHAP, and a closer look at errors. If not, stop at V1 and put the effort into the analysis and report.

### Roles, backup tasks, and the final split

If someone gets blocked, they switch to a backup task so everyone keeps producing.

| Who | Main task | Backup when stuck |
| --- | --- | --- |
| SHU Yi | Data integration and pipeline maintenance | Write up the data description; tidy the Kaggle submission flow. |
| CAO Yixin | EDA and feature engineering | Keep analyzing main-table variables; plot feature distributions. |
| ZHANG Yajing | Modeling, CV, and tuning | When no new features are coming in, improve the baseline and the CV framework. |
| SU Zhiyu | Evaluation, interpretation, and report | When there are no new results, write the methods section, prepare plotting functions, and tidy the project structure and references. |

Final split:

| Who | Final responsibility |
| --- | --- |
| SHU Yi | Data pipeline + baseline collaboration + Kaggle |
| CAO Yixin | EDA + feature engineering |
| ZHANG Yajing | Modeling + cross-validation + tuning |
| SU Zhiyu | Evaluation + SHAP/error analysis + report |

The report builds up from Phase 1. Suggested order: background → data → feature engineering → models → evaluation → results → discussion → member contributions. Each person submits the methods, results, and notes for their part, and SU Zhiyu merges them.

SHU Yi and CAO Yixin push the data and features forward, while ZHANG Yajing and SU Zhiyu get the model, evaluation, and report set up early. Once the shared data is ready, plug it into the existing pipelines. Everyone keeps at least one backup task that does not depend on anyone else's latest results.
