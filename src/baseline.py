"""V0 baseline; consumes raw application rows, including cleaning in the saved pipeline."""
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from data_pipeline import HomeCreditPreprocessor


def build_baseline(seed=42):
    return Pipeline([
        ('preprocess', HomeCreditPreprocessor()),
        ('classifier', LogisticRegression(C=1, solver='lbfgs', max_iter=2000, random_state=seed))
    ])
