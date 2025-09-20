from __future__ import annotations

import pandas as pd


def sample_dataframe(
    df: pd.DataFrame,
    *,
    sample_size: int | None = None,
    sample_percent: int | None = None,
    random_state: int = 9,
) -> pd.DataFrame:
    """Return a sampled view of a dataframe by size or percent.

    Args:
        df: Input dataframe.
        sample_size: Absolute number of rows to sample. If None, use sample_percent.
        sample_percent: Integer percent of rows to sample from 1 to 99.
        random_state: RNG seed for reproducibility.
    """
    if sample_size is not None and sample_percent is not None:
        raise ValueError("Provide only one of sample_size or sample_percent.")
    if sample_percent is not None:
        if not isinstance(sample_percent, int) or not (1 <= sample_percent <= 99):
            raise ValueError("sample_percent must be an integer between 1 and 99.")
        n = max(1, int(round((sample_percent / 100.0) * len(df))))
        sample_size = n
    if sample_size is None:
        sample_size = min(100, len(df))
    if sample_size <= 0 or sample_size >= len(df):
        return df
    return df.sample(n=sample_size, random_state=random_state)
