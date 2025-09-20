from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
from beartype import beartype
from MCPStack.core.tool.base import BaseTool

from .core import ToolState, sample_dataframe
from .services import AutoDDGService


@beartype
class AutoDDGTool(BaseTool):
    """MCP tool exposing the AutoDDG dataset description workflow."""

    def __init__(
        self,
        *,
        model_name: str = "gpt-4o-mini",
        search_model_name: str | None = None,
        semantic_model_name: str | None = None,
        description_words: int = 120,
        description_temperature: float = 0.0,
        topic_temperature: float = 0.0,
        evaluator_model_name: str = "gpt-4o",
        autoddg_factory: object | None = None,
        client_factory: object | None = None,
    ) -> None:
        super().__init__()
        self.service = AutoDDGService(
            model_name=model_name,
            search_model_name=search_model_name,
            semantic_model_name=semantic_model_name,
            description_words=description_words,
            description_temperature=description_temperature,
            topic_temperature=topic_temperature,
            evaluator_model_name=evaluator_model_name,
            autoddg_factory=autoddg_factory,
            client_factory=client_factory,
        )
        self._state = ToolState()
        self.required_env_vars = {
            "AUTO_DDG_OPENAI_API_KEY": "",
            "AUTO_DDG_EVALUATOR_API_KEY": "",
        }

    def _initialize(self) -> None:
        self.service.initialize()

    def _teardown(self) -> None:
        self.service.teardown()

    def _require_dataframe(self) -> pd.DataFrame:
        if self._state.dataframe is None:
            raise ValueError(
                "Load a dataset via `load_dataset` before running this action."
            )
        return self._state.dataframe

    def actions(self):
        return [
            self.load_dataset,
            self.profile_dataset,
            self.generate_semantic_profile,
            self.generate_topic,
            self.generate_description,
            self.expand_description_for_search,
            self.evaluate_description,
            self.get_state_summary,
        ]

    def load_dataset(
        self,
        *,
        csv_path: str | None = None,
        csv_text: str | None = None,
        sample_size: int | None = None,
        sample_percent: int | None = None,
        random_state: int = 9,
    ) -> dict[str, Any]:
        """Load a CSV dataset and store a sample by size or percent."""
        if bool(csv_path) == bool(csv_text):
            raise ValueError("Provide exactly one of `csv_path` or `csv_text`.")
        if csv_path is not None:
            dataframe = pd.read_csv(csv_path)
        else:
            dataframe = pd.read_csv(StringIO(csv_text or ""))
        sample_df = sample_dataframe(
            dataframe,
            sample_size=sample_size,
            sample_percent=sample_percent,
            random_state=random_state,
        )
        sample_csv = sample_df.to_csv(index=False)
        self._state = ToolState(dataframe=dataframe, sample_csv=sample_csv)
        return {
            "rows": len(dataframe),
            "columns": list(map(str, dataframe.columns)),
            "sample_size": len(sample_df),
            "sample_csv": sample_csv,
        }

    def profile_dataset(self) -> dict[str, Any]:
        """Run the datamart profiler on the loaded dataset."""
        dataframe = self._require_dataframe()
        profile_text, semantic_notes = self.service.profile_dataframe(dataframe)
        self._state.profile_text = profile_text
        self._state.semantic_profile = semantic_notes or self._state.semantic_profile
        return {"profile": profile_text, "semantic_notes": semantic_notes}

    def generate_semantic_profile(self) -> dict[str, Any]:
        """Infer semantic metadata for dataset columns using AutoDDG."""
        dataframe = self._require_dataframe()
        semantic_profile = self.service.analyze_semantics(dataframe)
        self._state.semantic_profile = semantic_profile
        return {"semantic_profile": semantic_profile}

    def generate_topic(
        self,
        *,
        title: str,
        original_description: str | None = None,
        dataset_sample: str | None = None,
    ) -> dict[str, Any]:
        """Generate a concise dataset topic."""
        sample = dataset_sample or self._state.sample_csv
        if not sample:
            raise ValueError(
                "Dataset sample not found. Load data before generating a topic."
            )
        topic = self.service.generate_topic(
            title=title,
            original_description=original_description,
            dataset_sample=sample,
        )
        self._state.topic = topic
        return {"topic": topic}

    def generate_description(
        self,
        *,
        dataset_sample: str | None = None,
        use_profile: bool = True,
        use_semantic_profile: bool = True,
        use_topic: bool = True,
    ) -> dict[str, Any]:
        """Generate a readable dataset description."""
        sample = dataset_sample or self._state.sample_csv
        if not sample:
            raise ValueError(
                "Dataset sample not found. Load data before generating a description."
            )
        profile_text = self._state.profile_text if use_profile else None
        semantic_profile = (
            self._state.semantic_profile if use_semantic_profile else None
        )
        topic = self._state.topic if use_topic else None
        if use_profile and profile_text is None:
            raise ValueError(
                "No dataset profile available. Run `profile_dataset` first or disable it."
            )
        if use_semantic_profile and semantic_profile is None:
            raise ValueError(
                "No semantic profile available. Run `generate_semantic_profile` first or disable it."
            )
        if use_topic and topic is None:
            raise ValueError(
                "No topic generated. Run `generate_topic` first or disable it."
            )
        prompt, description = self.service.describe_dataset(
            dataset_sample=sample,
            dataset_profile=profile_text,
            use_profile=use_profile and profile_text is not None,
            semantic_profile=semantic_profile,
            use_semantic_profile=use_semantic_profile and semantic_profile is not None,
            data_topic=topic,
            use_topic=use_topic and topic is not None,
        )
        self._state.description_prompt = prompt
        self._state.description_text = description
        return {"prompt": prompt, "description": description}

    def expand_description_for_search(self) -> dict[str, Any]:
        """Expand the last description into a search-focused variant."""
        if not self._state.description_text:
            raise ValueError("Generate a description before expanding it for search.")
        topic = self._state.topic
        if not topic:
            raise ValueError("Generate a topic before expanding for search.")
        prompt, expanded = self.service.expand_description_for_search(
            description=self._state.description_text, topic=topic
        )
        self._state.search_prompt = prompt
        self._state.search_description = expanded
        return {"prompt": prompt, "search_description": expanded}

    def evaluate_description(self) -> dict[str, Any]:
        """Evaluate the most recent dataset description using the configured evaluator."""
        if not self._state.description_text:
            raise ValueError("Generate a description before requesting an evaluation.")
        result = self.service.evaluate_description(self._state.description_text)
        return {"evaluation": result}

    def get_state_summary(self) -> dict[str, Any]:
        """Return a snapshot of the internal workflow state."""
        return {
            "has_dataset": self._state.dataframe is not None,
            "has_profile": self._state.profile_text is not None,
            "has_semantic_profile": self._state.semantic_profile is not None,
            "has_topic": self._state.topic is not None,
            "has_description": self._state.description_text is not None,
            "has_search_description": self._state.search_description is not None,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.service.model_name,
            "search_model_name": self.service.search_model_name,
            "semantic_model_name": self.service.semantic_model_name,
            "description_words": self.service.description_words,
            "description_temperature": self.service.description_temperature,
            "topic_temperature": self.service.topic_temperature,
            "evaluator_model_name": self.service.evaluator_model_name,
        }

    @classmethod
    def from_dict(cls, params: dict[str, Any]):
        return cls(**params)
