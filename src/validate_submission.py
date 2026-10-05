"""Validate a Home Credit submission without sending it anywhere (stdlib only)."""
import argparse
import csv
import math
from pathlib import Path

def read_ids(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if 'SK_ID_CURR' not in (reader.fieldnames or []):
            raise ValueError(f'{path}: missing SK_ID_CURR')
        ids = [row['SK_ID_CURR'] for row in reader]
    if not ids or any(not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError(f'{path}: empty, missing or duplicate IDs')
    return ids

def validate(submission, sample, test):
    sample_ids, test_ids = read_ids(sample), read_ids(test)
    if set(sample_ids) != set(test_ids):
        raise ValueError('Sample and test ID sets differ')
    with Path(submission).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['SK_ID_CURR', 'TARGET']:
            raise ValueError('Columns must be exactly SK_ID_CURR,TARGET')
        ids = []
        for row in reader:
            if None in row:
                raise ValueError('Unexpected extra fields')
            ids.append(row['SK_ID_CURR'])
            try:
                value = float(row['TARGET'])
            except (ValueError, TypeError):
                raise ValueError('TARGET must be numeric') from None
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError('TARGET must be finite and in [0,1]')
    if ids != sample_ids:
        raise ValueError('IDs/count/order must match sample_submission.csv')
    return f'PASS: {len(ids)} rows, unique matching IDs, correct columns, valid probabilities; nothing submitted.'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('submission', type=Path)
    parser.add_argument('--sample', type=Path, default=Path('data/raw/sample_submission.csv'))
    parser.add_argument('--test', type=Path, default=Path('data/raw/application_test.csv'))
    args = parser.parse_args()
    print(validate(args.submission, args.sample, args.test))
