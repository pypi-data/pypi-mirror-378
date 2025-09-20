from __future__ import annotations

import json
import os
from typing import Annotated

import typer
from beartype import beartype
from MCPStack.core.tool.cli.base import BaseToolCLI, ToolConfig
from rich.console import Console
from rich.panel import Panel

console = Console()


@beartype
class AutoDDGCLI(BaseToolCLI):
    """Typer-based helper for configuring the AutoDDG MCP tool."""

    @classmethod
    def get_app(cls) -> typer.Typer:
        app = typer.Typer(
            help="AutoDDG MCP tool CLI",
            add_completion=False,
            pretty_exceptions_show_locals=False,
            rich_markup_mode="markdown",
        )
        app.command(help="Show quick-start instructions for environment variables.")(
            cls.init
        )
        app.command(help="Generate a configuration file for the AutoDDG tool.")(
            cls.configure
        )
        app.command(help="Inspect current AutoDDG environment state.")(cls.status)
        return app

    @classmethod
    def init(
        cls,
        api_key: Annotated[
            str | None,
            typer.Option(
                "--api-key",
                "-k",
                help="OpenAI compatible API key used for dataset generation.",
            ),
        ] = None,
    ) -> None:
        api_key = api_key or os.getenv("AUTO_DDG_OPENAI_API_KEY") or "sk-..."
        console.print("[green]✅ AutoDDG quick-start[/green]")
        console.print(
            "Set the following environment variables before running the tool:\n"
        )
        console.print(f"    export AUTO_DDG_OPENAI_API_KEY='{api_key}'")
        console.print(
            "Optionally configure an evaluator key (defaults to the generation key if omitted):"
        )
        console.print(
            "    export AUTO_DDG_EVALUATOR_API_KEY='$AUTO_DDG_OPENAI_API_KEY'\n"
        )
        console.print("Update the placeholders with your actual credentials.")

    @classmethod
    def configure(
        cls,
        model_name: Annotated[
            str | None,
            typer.Option(
                "--model-name", "-m", help="Primary OpenAI model for generation."
            ),
        ] = None,
        search_model: Annotated[
            str | None,
            typer.Option(
                "--search-model", help="Model for search description expansion."
            ),
        ] = None,
        semantic_model: Annotated[
            str | None,
            typer.Option("--semantic-model", help="Model for semantic profiling."),
        ] = None,
        topic_temperature: Annotated[
            float | None,
            typer.Option(
                "--topic-temperature", help="Sampling temperature for topic generation."
            ),
        ] = None,
        description_words: Annotated[
            int | None,
            typer.Option(
                "--description-words", help="Target word count for descriptions."
            ),
        ] = None,
        description_temperature: Annotated[
            float | None,
            typer.Option(
                "--description-temperature",
                help="Temperature for description generation.",
            ),
        ] = None,
        api_key: Annotated[
            str | None,
            typer.Option("--api-key", help="OpenAI compatible API key."),
        ] = None,
        evaluator_key: Annotated[
            str | None,
            typer.Option("--evaluator-key", help="Optional evaluator API key."),
        ] = None,
        output: Annotated[
            str | None,
            typer.Option("--output", "-o", help="Path to save the JSON configuration."),
        ] = None,
        verbose: Annotated[
            bool,
            typer.Option("--verbose", "-v", help="Print the generated configuration."),
        ] = False,
    ) -> ToolConfig:
        env_vars: dict[str, str] = {}
        tool_params: dict[str, object] = {}

        if api_key is None:
            api_key = typer.prompt("AUTO_DDG_OPENAI_API_KEY", hide_input=True)
        env_vars["AUTO_DDG_OPENAI_API_KEY"] = api_key

        if evaluator_key is not None:
            env_vars["AUTO_DDG_EVALUATOR_API_KEY"] = evaluator_key

        if model_name is None:
            model_name = typer.prompt("Model name", default="gpt-4o-mini")
        tool_params["model_name"] = model_name

        if search_model:
            tool_params["search_model_name"] = search_model
        if semantic_model:
            tool_params["semantic_model_name"] = semantic_model
        if topic_temperature is not None:
            tool_params["topic_temperature"] = topic_temperature
        if description_words is not None:
            tool_params["description_words"] = description_words
        if description_temperature is not None:
            tool_params["description_temperature"] = description_temperature

        cfg: ToolConfig = {"env_vars": env_vars, "tool_params": tool_params}

        path = output or "autoddg_config.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

        console.print(f"[green]✅ Saved AutoDDG configuration to {path}[/green]")
        if verbose:
            console.print(
                Panel.fit(
                    json.dumps(cfg, indent=2),
                    title="[bold green]AutoDDG configuration[/bold green]",
                )
            )
        return cfg

    @classmethod
    def status(cls, verbose: bool = False) -> None:
        api_key = os.getenv("AUTO_DDG_OPENAI_API_KEY", "[not set]")
        evaluator_key = os.getenv("AUTO_DDG_EVALUATOR_API_KEY", "[not set]")
        panel = Panel.fit(
            f"AUTO_DDG_OPENAI_API_KEY: {api_key}\nAUTO_DDG_EVALUATOR_API_KEY: {evaluator_key}",
            title="[bold green]AutoDDG environment[/bold green]",
        )
        console.print(panel)
