from __future__ import annotations

import os
from typing import Any


class AutoDDGService:
    """Wrapper that manages client creation and calls to the AutoDDG library."""

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
        self.model_name = model_name
        self.search_model_name = search_model_name
        self.semantic_model_name = semantic_model_name
        self.description_words = description_words
        self.description_temperature = description_temperature
        self.topic_temperature = topic_temperature
        self.evaluator_model_name = evaluator_model_name
        self._autoddg_factory = autoddg_factory
        self._client_factory = client_factory
        self._client: Any | None = None
        self._autoddg: Any | None = None

    def initialize(self) -> None:
        self._client = None
        if self._autoddg_factory is None:
            self._autoddg = None

    def teardown(self) -> None:
        self._client = None
        self._autoddg = None

    def ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = os.getenv("AUTO_DDG_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "AutoDDG requires an OpenAI compatible API key. Set AUTO_DDG_OPENAI_API_KEY "
                "or OPENAI_API_KEY before invoking generative actions."
            )
        if self._client_factory is not None:
            self._client = self._client_factory(api_key)  # type: ignore[misc]
        else:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key)
        return self._client

    def ensure_autoddg(self) -> Any:
        if self._autoddg is not None:
            return self._autoddg
        client = self.ensure_client()
        if self._autoddg_factory is not None:
            self._autoddg = self._autoddg_factory(
                client=client,
                model_name=self.model_name,
                description_temperature=self.description_temperature,
                description_words=self.description_words,
                search_model_name=self.search_model_name,
                semantic_model_name=self.semantic_model_name,
                topic_temperature=self.topic_temperature,
            )
        else:
            from autoddg import AutoDDG

            self._autoddg = AutoDDG(
                client=client,
                model_name=self.model_name,
                description_temperature=self.description_temperature,
                description_words=self.description_words,
                search_model_name=self.search_model_name,
                semantic_model_name=self.semantic_model_name,
                topic_temperature=self.topic_temperature,
            )
        return self._autoddg

    def attach_default_evaluator(self) -> None:
        autoddg_obj = self.ensure_autoddg()
        if getattr(autoddg_obj, "evaluator", None) is not None:
            return
        evaluator_key = os.getenv("AUTO_DDG_EVALUATOR_API_KEY") or os.getenv(
            "AUTO_DDG_OPENAI_API_KEY"
        )
        if not evaluator_key:
            raise RuntimeError(
                "AutoDDG evaluator requires AUTO_DDG_EVALUATOR_API_KEY (or reuse AUTO_DDG_OPENAI_API_KEY)."
            )
        if not hasattr(autoddg_obj, "set_evaluator"):
            raise RuntimeError(
                "The underlying AutoDDG instance does not support evaluators."
            )
        if self._autoddg_factory is not None:
            autoddg_obj.set_evaluator("AUTO")
        else:
            from autoddg import GPTEvaluator

            autoddg_obj.set_evaluator(
                GPTEvaluator(
                    gpt4_api_key=evaluator_key, model_name=self.evaluator_model_name
                )
            )

    def profile_dataframe(self, df):
        return self.ensure_autoddg().profile_dataframe(df)

    def analyze_semantics(self, df):
        return self.ensure_autoddg().analyze_semantics(df)

    def generate_topic(
        self, *, title: str, original_description: str | None, dataset_sample: str
    ):
        return self.ensure_autoddg().generate_topic(
            title=title,
            original_description=original_description,
            dataset_sample=dataset_sample,
        )

    def describe_dataset(
        self,
        *,
        dataset_sample: str,
        dataset_profile: str | None,
        use_profile: bool,
        semantic_profile: str | None,
        use_semantic_profile: bool,
        data_topic: str | None,
        use_topic: bool,
    ):
        return self.ensure_autoddg().describe_dataset(
            dataset_sample=dataset_sample,
            dataset_profile=dataset_profile,
            use_profile=use_profile,
            semantic_profile=semantic_profile,
            use_semantic_profile=use_semantic_profile,
            data_topic=data_topic,
            use_topic=use_topic,
        )

    def expand_description_for_search(self, *, description: str, topic: str):
        return self.ensure_autoddg().expand_description_for_search(
            description=description, topic=topic
        )

    def evaluate_description(self, description: str):
        self.attach_default_evaluator()
        return self.ensure_autoddg().evaluate_description(description)
