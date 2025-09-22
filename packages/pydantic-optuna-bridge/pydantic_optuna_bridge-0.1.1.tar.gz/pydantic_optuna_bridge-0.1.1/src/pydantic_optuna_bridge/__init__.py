"""Bridge Pydantic hyperparameter schemas to Optuna distributions.

Example:
    uv run -m pydantic_optuna_bridge.metadata --help
"""

from .metadata import (
    OptunaMetadata,
    attach_optuna_metadata,
    derive_optuna_metadata,
    get_search_space,
    optuna_config,
    suggest_from_config,
    validate_search_space,
)

__all__ = [
    "OptunaMetadata",
    "derive_optuna_metadata",
    "attach_optuna_metadata",
    "optuna_config",
    "suggest_from_config",
    "get_search_space",
    "validate_search_space",
]
