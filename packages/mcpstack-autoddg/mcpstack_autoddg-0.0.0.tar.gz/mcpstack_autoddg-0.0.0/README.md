<!--suppress HtmlDeprecatedAttribute -->
<div align="center">
  <h1 align="center">
    <br>
    <a href="#"><img src="assets/COVER.png" alt="MCPStack Tool" width="100%"></a>
    <br>
    MCPStack AutoDDG MCP
    <br>
  </h1>
  <h4 align="center">Automatic dataset topics & descriptions — powered by AutoDDG and MCPStack</h4>
</div>

<div align="center">

<a href="https://pre-commit.com/">
  <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-1f6feb?style=for-the-badge&logo=pre-commit">
</a>
<img alt="ruff" src="https://img.shields.io/badge/Ruff-lint%2Fformat-9C27B0?style=for-the-badge&logo=ruff&logoColor=white">
<img alt="python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img alt="license" src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge">

</div>

> [!IMPORTANT]
> If you haven’t visited the MCPStack main orchestrator repository yet, please start
> there: **[MCPStack](https://github.com/MCP-Pipeline/MCPStack)**

> [!CAUTION]
> Please be aware that this MCP is in an early-alpha stage. While it is functional and can be used for various tasks, it may still contain bugs or incomplete features.
> Feel free to report any issues you encounter or suggest improvements. Even better, feel free to contribute directly!

> [!WARNING]
> Please be aware that you cannot use this MCP without an OpenAI-compatible API key.
> To gen. one, please visit: https://platform.openai.com/account/api-keys

> [!NOTE]
> For the time being, this MCP is working with the branch `feat/modern_pythonic_library_transformation` from the
> mother library, AutoDDG. See more at: https://github.com/VIDA-NYU/AutoDDG/pull/4.
> As such, we recommend you to install AutoDDG from source with this library, until the PR is merged upstream.
> Adapt the "autoddg" in the dependencies in `pyproject.toml` accordingly.

## 💡 About The MCPStack AutoDDG Tool

This repository provides a **native MCP** around the **AutoDDG** library for dataset description and discovery:

- Load a CSV and keep a **deterministic sample** (by size or percentage).
- **Profile** a dataframe ([datamart-style](https://pypi.org/project/datamart-profiler/) notes).
- Infer a **semantic profile** for columns.
- Generate a concise **topic**.
- Produce a readable **dataset description**.
- Expand that description for **search/discovery** (tune the `temperature` etc.).
- Optionally **evaluate** the description with a separate evaluator key.

AutoDDG official library (without the MCP wrapper): https://github.com/VIDA-NYU/AutoDDG

## Installation

The tool is distributed as a standard Python package. MCPStack will auto-discover it.

### Via `uv` (recommended)

```bash
uv add mcpstack-autoddg
```

### Via pip
```bash
pip install mcpstack-autoddg
```

###  (Dev) Pre-commit hooks

```bash
uv run pre-commit install
# or: pre-commit install
```


## Using With MCPStack — CLI workflow

This tool declares entry points so MCPStack can see it automatically:

```toml
[project.entry-points."mcpstack.tools"]
autoddgtool = "mcpstack_autoddg.tool:AutoDDGTool"

[project.entry-points."mcpstack.tool_clis"]
autoddgtool = "mcpstack_autoddg.cli:AutoDDGCLI.get_app"
```

### 1) (Optional) Configure environment

AutoDDG requires an OpenAI-compatible key. You may optionally provide a separate evaluator key:

```
AUTO_DDG_OPENAI_API_KEY: "<your key>" (required for generation)
AUTO_DDG_EVALUATOR_API_KEY: "<your key>" (optional; falls back to AUTO_DDG_OPENAI_API_KEY)
```

Use the CLI to generate a config file (useful for CI or sharing defaults):

```bash
uv run mcpstack tools autoddg configure
# Then is followed an interactive prompt to config and set parameters.
```

Or you can pass parameters directly, e.g.:
```bash
uv run mcpstack tools autoddg configure \
  --model-name gpt-4o-mini \
  --description-words 120 \
  --description-temperature 0.0 \
  --topic-temperature 0.0 \
  --api-key sk-... \
  --evaluator-key sk-... \
  -o autoddg_config.json \
  --verbose
```

For others, feel free to `uv run mcpstack tools autoddg --help` to see all options.

### 2) Add to a pipeline

Create or extend a pipeline with AutoDDG:

```bash
# New pipeline
uv run mcpstack pipeline autoddg --new-pipeline my_pipeline.json --tool-config autoddg_config.json
```

```bash
# Or append to an existing one
uv run mcpstack pipeline autoddg --to-pipeline my_pipeline.json --tool-config autoddg_config.json
```


## Programmatic API Workflow

Use the AutoDDG tool directly in a stack:

```python
from MCPStack.stack import MCPStackCore
from mcpstack_autoddg import AutoDDGTool

pipeline = (
    MCPStackCore()
    .with_tool(AutoDDGTool(
        model_name="gpt-4o-mini",
        search_model_name=None,
        semantic_model_name=None,
        description_words=120,
        description_temperature=0.0,
        topic_temperature=0.0,
        evaluator_model_name="gpt-4o",
    ))
    .build(type="fastmcp", save_path="autoddg_pipeline.json")
    .run()
)
```

### AutoDDG Actions Supported

> [!NOTE]
> If any action fails, feel free to open an issue so we may update with the
> potential changes on the mother library, AutoDDG.
> https://github.com/VIDA-NYU/AutoDDG

* `load_dataset(csv_path|csv_text, sample_size?, sample_percent?, random_state=9)` → load CSV and store a sampled CSV string in state
* `profile_dataset()` → datamart-like profile; may also return semantic notes
* `generate_semantic_profile()` → infer semantic metadata for columns
* `generate_topic(title, original_description?, dataset_sample?)` → concise dataset topic
* `generate_description(dataset_sample?, use_profile=True, use_semantic_profile=True, use_topic=True)` → readable description; enforces prerequisites if the flags are left on
* `expand_description_for_search()` → search-oriented variant of the last description (needs a topic)
* `evaluate_description()` → runs evaluator (requires evaluator key or reuse of generation key)
* `get_state_summary()` → booleans for which artifacts exist in state


## License

MIT — see **[LICENSE](LICENSE)**.
