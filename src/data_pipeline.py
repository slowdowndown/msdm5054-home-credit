"""Shared V0 loader, fixed split and train-only preprocessing.

Import from src after adding it to sys.path. Saved pipelines require this module.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted


def verify_file(path, expected):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != expected:
        raise ValueError(f'Data version mismatch: {Path(path).name}')


def load_main_tables(root):
    root = Path(root)
    manifest = json.loads((root/'docs/data/data_manifest_v0.json').read_text())
    for name in ['application_train.csv', 'application_test.csv',
                 'HomeCredit_columns_description.csv', 'sample_submission.csv']:
        verify_file(root/'data/raw'/name, manifest[name]['sha256'])
    train = pd.read_csv(root/'data/raw/application_train.csv')
    test = pd.read_csv(root/'data/raw/application_test.csv')
    dictionary = pd.read_csv(root/'data/raw/HomeCredit_columns_description.csv', encoding='cp1252')
    if not train.SK_ID_CURR.is_unique or not test.SK_ID_CURR.is_unique:
        raise ValueError('Duplicate application IDs')
    if set(train.SK_ID_CURR) & set(test.SK_ID_CURR):
        raise ValueError('Train/test IDs overlap')
    if not train.TARGET.isin([0, 1]).all():
        raise ValueError('Invalid TARGET')
    if set(train.columns)-{'TARGET'} != set(test.columns):
        raise ValueError('Train/test schemas differ')
    return train, test, dictionary


def fixed_split(root, train=None):
    root = Path(root)
    cfg = json.loads((root/'docs/data/split_protocol.json').read_text())
    path = root/cfg['input']
    verify_file(path, cfg['input_sha256'])
    labels = pd.read_csv(path, usecols=['SK_ID_CURR', 'TARGET'])
    if train is not None and not labels.equals(train[['SK_ID_CURR', 'TARGET']].reset_index(drop=True)):
        raise ValueError('Input rows/labels do not match the canonical training file')
    fit_idx, val_idx = train_test_split(np.arange(len(labels)),
        test_size=cfg['validation_fraction'], random_state=cfg['seed'], stratify=labels.TARGET)
    if (len(fit_idx), len(val_idx)) != (cfg['train_rows'], cfg['validation_rows']):
        raise ValueError('Unexpected split size')
    assignments = labels[['SK_ID_CURR']].copy()
    assignments['split'] = 'train'
    assignments.loc[val_idx, 'split'] = 'validation'
    output = root/cfg['output']
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        existing = pd.read_csv(output)
        if not existing.equals(assignments):
            raise ValueError('Existing split differs; refusing to overwrite')
    else:
        assignments.to_csv(output, index=False)
    return fit_idx, val_idx, assignments


def deterministic_clean(frame):
    frame = frame.drop(columns=['TARGET', 'SK_ID_CURR'], errors='ignore').copy()
    frame['DAYS_EMPLOYED'] = frame['DAYS_EMPLOYED'].replace(365243, np.nan)
    for col in ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE']:
        frame[col] = np.log1p(frame[col].where(frame[col] >= 0))
    return frame


class HomeCreditPreprocessor(TransformerMixin, BaseEstimator):
    """Learns column selection/imputation/encoding only during fit, including CV folds."""
    def __init__(self, missing_threshold=0.8):
        self.missing_threshold = missing_threshold

    def fit(self, X, y=None):
        clean = deterministic_clean(X)
        self.dropped_ = clean.columns[clean.isna().mean() > self.missing_threshold].tolist()
        kept = clean.drop(columns=self.dropped_)
        self.numeric_ = kept.select_dtypes(include='number').columns.tolist()
        self.categorical_ = kept.select_dtypes(exclude='number').columns.tolist()
        self.transformer_ = ColumnTransformer([
            ('numeric', Pipeline([('impute', SimpleImputer(strategy='median', add_indicator=True)),
                                  ('scale', StandardScaler())]), self.numeric_),
            ('category', Pipeline([('impute', SimpleImputer(strategy='constant', fill_value='Missing')),
                                   ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=True))]),
             self.categorical_)], sparse_threshold=1.0)
        self.transformer_.fit(clean, y)
        return self

    def transform(self, X):
        check_is_fitted(self, 'transformer_')
        return self.transformer_.transform(deterministic_clean(X))

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, 'transformer_')
        return self.transformer_.get_feature_names_out()
