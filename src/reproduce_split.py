"""Verify source data and rebuild the agreed split without changing an existing split."""
from pathlib import Path
from data_pipeline import fixed_split

if __name__ == '__main__':
    _, _, assignments = fixed_split(Path(__file__).resolve().parents[1])
    print(assignments['split'].value_counts().to_string())
