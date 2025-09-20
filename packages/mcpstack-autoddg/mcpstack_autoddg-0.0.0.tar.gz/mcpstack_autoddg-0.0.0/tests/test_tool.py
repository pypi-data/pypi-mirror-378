from __future__ import annotations

from typing import Any

from MCPStack.cli import StackCLI
from typer.testing import CliRunner

from mcpstack_autoddg.tool import AutoDDGTool

runner = CliRunner()
app = StackCLI().app


class StubAutoDDG:
    def __init__(self, **_: Any) -> None:
        self.evaluator = None

    def profile_dataframe(self, dataframe):
        assert not dataframe.empty
        return "PROFILE", "SEMANTIC NOTES"

    def analyze_semantics(self, dataframe):
        assert not dataframe.empty
        return "SEMANTIC PROFILE"

    def generate_topic(
        self, title: str, original_description: str | None, dataset_sample: str
    ) -> str:
        assert title
        assert dataset_sample
        return "Stub Topic"

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
    ) -> tuple[str, str]:
        assert dataset_sample
        if use_profile:
            assert dataset_profile == "PROFILE"
        if use_semantic_profile:
            assert semantic_profile == "SEMANTIC PROFILE"
        if use_topic:
            assert data_topic == "Stub Topic"
        return "PROMPT", "DESCRIPTION"

    def expand_description_for_search(
        self, *, description: str, topic: str
    ) -> tuple[str, str]:
        assert description
        assert topic
        return "SPROMPT", "SEARCH DESC"

    def evaluate_description(self, description: str) -> str:
        if self.evaluator is None:
            raise RuntimeError("missing evaluator")
        return f"EVAL:{description}"

    def set_evaluator(self, evaluator: Any) -> None:
        self.evaluator = evaluator


def build_tool(monkeypatch) -> AutoDDGTool:
    monkeypatch.setenv("AUTO_DDG_OPENAI_API_KEY", "test-key")
    tool = AutoDDGTool(
        autoddg_factory=lambda **kwargs: StubAutoDDG(**kwargs),
        client_factory=lambda api_key: {"api_key": api_key},
    )
    tool.initialize()
    return tool


def test_actions() -> None:
    tool = AutoDDGTool(
        autoddg_factory=lambda **kwargs: StubAutoDDG(**kwargs),
        client_factory=lambda api_key: {"api_key": api_key},
    )
    action_names = [fn.__name__ for fn in tool.actions()]
    assert action_names == [
        "load_dataset",
        "profile_dataset",
        "generate_semantic_profile",
        "generate_topic",
        "generate_description",
        "expand_description_for_search",
        "evaluate_description",
        "get_state_summary",
    ]


def test_dataset_workflow(monkeypatch) -> None:
    tool = build_tool(monkeypatch)
    load_result = tool.load_dataset(
        csv_text="name,age\nAlice,30\nBob,25", sample_size=1, random_state=42
    )
    assert load_result["rows"] == 2
    assert load_result["sample_size"] == 1

    profile = tool.profile_dataset()
    assert profile["profile"] == "PROFILE"

    semantic = tool.generate_semantic_profile()
    assert semantic["semantic_profile"] == "SEMANTIC PROFILE"

    topic = tool.generate_topic(title="Test Dataset")
    assert topic["topic"] == "Stub Topic"

    description = tool.generate_description()
    assert description["description"] == "DESCRIPTION"

    search = tool.expand_description_for_search()
    assert search["search_description"] == "SEARCH DESC"

    monkeypatch.setenv("AUTO_DDG_EVALUATOR_API_KEY", "test-key")
    evaluation = tool.evaluate_description()
    assert evaluation["evaluation"].startswith("EVAL:")

    summary = tool.get_state_summary()
    assert summary["has_search_description"] is True


def test_tool_cli_mounts() -> None:
    result = runner.invoke(app, ["tools", "autoddg", "--help"])
    assert result.exit_code in (0, 2)
