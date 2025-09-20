from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ToolState:
    """Lightweight in-memory state between actions."""

    dataframe: pd.DataFrame | None = None
    sample_csv: str | None = None
    profile_text: str | None = None
    semantic_profile: str | None = None
    topic: str | None = None
    description_prompt: str | None = None
    description_text: str | None = None
    search_prompt: str | None = None
    search_description: str | None = None
