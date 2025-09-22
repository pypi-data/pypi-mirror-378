"""CLI facade for the demo Optuna metadata generator.

Example:
    uv run -m pydantic_optuna_bridge --help
"""

from .metadata import _run_demo_cli


if __name__ == "__main__":
    _run_demo_cli()
