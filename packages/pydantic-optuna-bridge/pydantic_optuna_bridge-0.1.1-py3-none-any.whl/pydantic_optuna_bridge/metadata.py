"""Automatic Optuna configuration from Pydantic field constraints.

This module inspects constrained Pydantic models and surfaces Optuna-compatible
search space metadata. The ``@optuna_config`` decorator wires the generated
metadata back onto the model, ensuring hyperparameter validation and sampling
stay in sync.

Example:
    >>> from enum import Enum
    >>> from typing import Annotated
    >>> from pydantic import BaseModel, Field
    >>>
    >>> class Scheduler(str, Enum):
    ...     COSINE = "cosine"
    ...     EXP = "exp"
    ...     STEP = "step"
    >>>
    >>> @optuna_config(
    ...     log_scale_fields={"learning_rate", "weight_decay"},
    ...     categorical_field_weights={"scheduler": [0.5, 0.3, 0.2]},
    ... )
    ... class MLPConfig(BaseModel):
    ...     learning_rate: Annotated[float, Field(ge=1e-5, le=1e-2)]
    ...     weight_decay: Annotated[float, Field(ge=1e-6, le=1e-2)]
    ...     epochs: Annotated[int, Field(ge=10, le=100)]
    ...     scheduler: Scheduler
    >>>
    >>> # Optuna can now reconstruct the config straight from a trial:
    >>> # trial -> MLPConfig.from_optuna_trial(trial)
"""

import types
from collections.abc import Sequence
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING, Annotated, Any, Union, get_args, get_origin, get_type_hints

from annotated_types import Ge, Gt, Le, Lt
from pydantic import BaseModel
from pydantic.fields import FieldInfo

if TYPE_CHECKING:  # pragma: no cover
    import optuna

OptunaMetadata = dict[str, dict[str, Any]]

_OPTUNA_METADATA_ATTR = "__optuna_metadata__"

__all__ = [
    "OptunaMetadata",
    "derive_optuna_metadata",
    "attach_optuna_metadata",
    "optuna_config",
    "suggest_from_config",
    "get_search_space",
    "validate_search_space",
]


def derive_optuna_metadata(
    model_cls: type[BaseModel],
    *,
    log_scale_fields: set[str] | None = None,
    categorical_field_weights: dict[str, list[float]] | None = None,
) -> OptunaMetadata:
    """Derive Optuna distributions from field constraints on ``model_cls``.

    Args:
        model_cls: Pydantic model defining hyperparameters.
        log_scale_fields: Field names that should explore float ranges in log space.
        categorical_field_weights: Optional sampling weights for enum-backed fields.

    Returns:
        Mapping of field names to Optuna distribution metadata.
    """

    assert issubclass(model_cls, BaseModel), "model_cls must inherit from BaseModel"

    log_fields = log_scale_fields or set()
    weights = categorical_field_weights or {}

    hints = get_type_hints(model_cls, include_extras=True)
    metadata: OptunaMetadata = {}

    for field_name, field_info in model_cls.model_fields.items():
        annotation = hints.get(field_name)
        if annotation is None:
            continue

        base_type = _unwrap_annotation(annotation)
        if base_type is None:
            continue

        optuna_payload = _build_metadata_for_field(
            field_name,
            base_type,
            field_info,
            log_fields,
            weights,
        )

        if optuna_payload is not None:
            metadata[field_name] = optuna_payload

    unknown_log = log_fields.difference(metadata)
    assert not unknown_log, f"Log-scale fields not found or unsupported: {sorted(unknown_log)}"

    unknown_weights = set(weights).difference(metadata)
    assert not unknown_weights, f"Weighted categorical fields not found: {sorted(unknown_weights)}"

    return metadata


def attach_optuna_metadata(model_cls: type[BaseModel], metadata: OptunaMetadata) -> None:
    """Attach Optuna metadata to ``json_schema_extra`` for later consumers."""

    for field_name, optuna_payload in metadata.items():
        assert field_name in model_cls.model_fields, f"Unknown field: {field_name}"
        field_info = model_cls.model_fields[field_name]
        assert not field_info.json_schema_extra, (
            f"Field '{field_name}' already defines json_schema_extra; refusing to overwrite"
        )
        field_info.json_schema_extra = {"optuna": dict(optuna_payload)}


def optuna_config(
    *,
    log_scale_fields: set[str] | None = None,
    categorical_field_weights: dict[str, list[float]] | None = None,
):
    """Decorator that wires Optuna metadata and convenience helpers onto a model."""

    def decorator(model_cls: type[BaseModel]) -> type[BaseModel]:
        metadata = derive_optuna_metadata(
            model_cls,
            log_scale_fields=log_scale_fields,
            categorical_field_weights=categorical_field_weights,
        )
        attach_optuna_metadata(model_cls, metadata)

        frozen_metadata = MappingProxyType({name: dict(payload) for name, payload in metadata.items()})

        assert not hasattr(model_cls, _OPTUNA_METADATA_ATTR), "Model already defines __optuna_metadata__"
        setattr(model_cls, _OPTUNA_METADATA_ATTR, frozen_metadata)

        assert not hasattr(model_cls, "optuna_metadata"), "Model already defines optuna_metadata"

        @classmethod
        def optuna_metadata(cls) -> OptunaMetadata:
            metadata_ref: MappingProxyType[str, dict[str, Any]] = getattr(cls, _OPTUNA_METADATA_ATTR)
            return {name: dict(payload) for name, payload in metadata_ref.items()}

        setattr(model_cls, "optuna_metadata", optuna_metadata)

        assert not hasattr(model_cls, "from_optuna_trial"), "Model already defines from_optuna_trial"

        @classmethod
        def from_optuna_trial(cls, trial: Any, /, **overrides: Any) -> BaseModel:
            metadata_ref: MappingProxyType[str, dict[str, Any]] = getattr(cls, _OPTUNA_METADATA_ATTR)
            params = _suggest_parameters(trial, metadata_ref, overrides)
            return cls(**params)

        setattr(model_cls, "from_optuna_trial", from_optuna_trial)

        return model_cls

    return decorator


def _unwrap_annotation(annotation: object) -> type[object] | None:
    origin = get_origin(annotation)

    if origin is Annotated:
        return _unwrap_annotation(get_args(annotation)[0])

    if origin in (types.UnionType, Union):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _unwrap_annotation(args[0])
        return None

    return annotation if isinstance(annotation, type) else None


def _build_metadata_for_field(
    field_name: str,
    base_type: type[object],
    field_info: FieldInfo,
    log_fields: set[str],
    weights: dict[str, list[float]],
) -> dict[str, Any] | None:
    if isinstance(base_type, type) and issubclass(base_type, Enum):
        return _enum_metadata(field_name, base_type, weights)

    if base_type is int:
        return _numeric_metadata(field_name, field_info, base_type, log_fields)

    if base_type is float:
        return _numeric_metadata(field_name, field_info, base_type, log_fields)

    return None


def _enum_metadata(
    field_name: str,
    enum_cls: type[Enum],
    weights: dict[str, list[float]],
) -> dict[str, Any]:
    choices = [member.value for member in enum_cls]
    payload: dict[str, Any] = {"distribution": "categorical", "choices": choices}

    if field_name in weights:
        field_weights = weights[field_name]
        assert len(field_weights) == len(choices), f"Weights for '{field_name}' must match number of choices"
        payload["weights"] = list(field_weights)

    return payload


def _numeric_metadata(
    field_name: str,
    field_info: FieldInfo,
    base_type: type[object],
    log_fields: set[str],
) -> dict[str, Any]:
    bounds = _extract_bounds(field_name, field_info, base_type)
    payload: dict[str, Any] = {"low": bounds[0], "high": bounds[1]}
    payload["distribution"] = "int" if base_type is int else "float"

    if field_name in log_fields:
        assert base_type is float, f"Log scale only valid for float fields: {field_name}"
        payload["log"] = True

    return payload


def _extract_bounds(  # noqa: C901
    field_name: str,
    field_info: FieldInfo,
    base_type: type[object],
) -> tuple[float, float]:
    lower: float | None = None
    upper: float | None = None

    for constraint in getattr(field_info, "metadata", ()):  # type: ignore[attr-defined]
        if isinstance(constraint, Ge):
            lower = _max_value(lower, constraint.ge)
        elif isinstance(constraint, Gt):
            bound = constraint.gt + 1 if base_type is int else constraint.gt
            lower = _max_value(lower, bound)
        elif isinstance(constraint, Le):
            upper = _min_value(upper, constraint.le)
        elif isinstance(constraint, Lt):
            bound = constraint.lt - 1 if base_type is int else constraint.lt
            upper = _min_value(upper, bound)

    assert lower is not None, f"Field '{field_name}' must define a lower bound"
    assert upper is not None, f"Field '{field_name}' must define an upper bound"
    assert lower < upper, f"Field '{field_name}' has invalid bounds: lower={lower}, upper={upper}"

    return lower, upper


def _max_value(current: float | None, candidate: float) -> float:
    if current is None or candidate > current:
        return candidate
    return current


def _min_value(current: float | None, candidate: float) -> float:
    if current is None or candidate < current:
        return candidate
    return current


def _suggest_parameters(
    trial: Any,
    metadata: MappingProxyType[str, dict[str, Any]] | OptunaMetadata,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    overrides = overrides or {}

    for field_name, payload in metadata.items():
        if field_name in overrides:
            params[field_name] = overrides[field_name]
            continue

        distribution = payload.get("distribution")
        assert isinstance(distribution, str), f"Invalid distribution for field '{field_name}'"

        if distribution == "categorical":
            suggest = getattr(trial, "suggest_categorical", None)
            assert callable(suggest), "Trial missing suggest_categorical"
            choices = payload.get("choices")
            assert isinstance(choices, list), f"Field '{field_name}' lacks categorical choices"
            weighted_choices = _expand_weighted_choices(choices, payload.get("weights"))
            params[field_name] = suggest(field_name, weighted_choices)
            continue

        if distribution == "float":
            suggest = getattr(trial, "suggest_float", None)
            assert callable(suggest), "Trial missing suggest_float"
            low = float(payload["low"])
            high = float(payload["high"])
            log_flag = bool(payload.get("log"))
            params[field_name] = suggest(field_name, low, high, log=log_flag)
            continue

        if distribution == "int":
            suggest = getattr(trial, "suggest_int", None)
            assert callable(suggest), "Trial missing suggest_int"
            low = int(payload["low"])
            high = int(payload["high"])
            params[field_name] = suggest(field_name, low, high)
            continue

        raise AssertionError(f"Unsupported Optuna distribution: {distribution}")

    return params


def _expand_weighted_choices(choices: Sequence[Any], weights: Sequence[float] | None) -> list[Any]:
    if weights is None:
        return list(choices)

    assert len(weights) == len(choices), "Weights must align with categorical choices"
    total = sum(weights)
    assert total > 0, "Categorical weights must sum to a positive value"

    scale = max(len(choices), 100)
    expanded: list[Any] = []
    for choice, weight in zip(choices, weights, strict=True):
        proportion = weight / total
        count = max(1, round(proportion * scale))
        expanded.extend([choice] * int(count))

    return expanded


def suggest_from_config(
    trial: Any,
    model_cls: type[BaseModel],
    /,
    **overrides: Any,
) -> dict[str, Any]:
    """Sample parameters for ``model_cls`` using the Optuna trial."""

    assert hasattr(model_cls, _OPTUNA_METADATA_ATTR), (
        f"Model '{model_cls.__name__}' is not decorated with @optuna_config"
    )

    metadata_ref: MappingProxyType[str, dict[str, Any]] = getattr(model_cls, _OPTUNA_METADATA_ATTR)
    return _suggest_parameters(trial, metadata_ref, overrides)


def get_search_space(model_cls: type[BaseModel]) -> OptunaMetadata:
    """Expose the Optuna search space declared on ``model_cls``."""

    assert hasattr(model_cls, _OPTUNA_METADATA_ATTR), (
        f"Model '{model_cls.__name__}' is not decorated with @optuna_config"
    )

    metadata_ref: MappingProxyType[str, dict[str, Any]] = getattr(model_cls, _OPTUNA_METADATA_ATTR)
    return {name: dict(payload) for name, payload in metadata_ref.items()}


def validate_search_space(model_cls: type[BaseModel]) -> list[str]:
    """Validate that the Optuna search space on ``model_cls`` is well defined."""

    warnings: list[str] = []
    search_space = get_search_space(model_cls)

    for field_name, payload in search_space.items():
        distribution = payload.get("distribution")
        assert isinstance(distribution, str), f"Field '{field_name}' missing distribution type"

        if distribution in {"int", "float"}:
            if "low" not in payload:
                warnings.append(f"{field_name}: missing lower bound")
            if "high" not in payload:
                warnings.append(f"{field_name}: missing upper bound")
            low = payload.get("low")
            high = payload.get("high")
            if isinstance(low, (int, float)) and isinstance(high, (int, float)):
                if low >= high:
                    warnings.append(f"{field_name}: lower bound >= upper bound ({low} >= {high})")

        elif distribution == "categorical":
            choices = payload.get("choices")
            if not isinstance(choices, list) or not choices:
                warnings.append(f"{field_name}: categorical distribution missing choices")
            weights = payload.get("weights")
            if weights is not None and len(weights) != len(choices or []):
                warnings.append(
                    f"{field_name}: weights length {len(weights)} != choices length {len(choices or [])}"
                )

        else:
            warnings.append(f"{field_name}: unsupported distribution '{distribution}'")

    return warnings


def _run_demo_cli() -> None:
    import json
    import sys

    import click
    from loguru import logger
    from rich.console import Console
    from rich.table import Table

    class DemoOptimizer(str, Enum):
        ADAM = "adam"
        SGD = "sgd"
        RMSPROP = "rmsprop"

    class DemoConfig(BaseModel):
        optimizer: DemoOptimizer
        learning_rate: Annotated[float, Gt(1e-5), Lt(1.0)]
        hidden_units: Annotated[int, Ge(32), Le(256)]

    console = Console()

    @click.command()
    def main() -> None:
        """Generate and pretty-print Optuna metadata for a demo schema."""

        metadata = derive_optuna_metadata(
            DemoConfig,
            log_scale_fields={"learning_rate"},
            categorical_field_weights={"optimizer": [0.5, 0.3, 0.2]},
        )
        attach_optuna_metadata(DemoConfig, metadata)

        table = Table(title="Derived Optuna Metadata")
        table.add_column("Field")
        table.add_column("Payload")

        for field_name, payload in metadata.items():
            table.add_row(field_name, json.dumps(payload, indent=2))

        console.print(table)

    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    main()


if __name__ == "__main__":
    _run_demo_cli()
