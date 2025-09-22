"""Bridge Pydantic hyperparameter schemas to Optuna distributions.

Example:
    uv run -m pydantic_optuna_bridge.metadata --help
"""

from .metadata import OptunaMetadata, attach_optuna_metadata, derive_optuna_metadata

__all__ = [
    "OptunaMetadata",
    "derive_optuna_metadata",
    "attach_optuna_metadata",
]
