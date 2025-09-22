# pydantic-optuna-bridge

Derive Optuna distributions directly from constrained Pydantic models. This
project extracts the metadata helpers originally used in the
[`kaggle-map`](https://github.com/alexdong/kaggle-map) repository so that the
utilities can be reused across projects.

## Installation

```bash
uv add pydantic-optuna-bridge
# or
pip install pydantic-optuna-bridge
```

Install the optional CLI dependencies if you plan to use the demo command:

```bash
uv add pydantic-optuna-bridge[cli]
```

## Usage

Create a Pydantic model that constrains your hyperparameters and derive the
Optuna metadata:

```python
from enum import Enum
from typing import Annotated

from annotated_types import Ge, Gt, Le, Lt
from pydantic import BaseModel

from pydantic_optuna_bridge import attach_optuna_metadata, derive_optuna_metadata


class Optimizer(str, Enum):
    ADAM = "adam"
    SGD = "sgd"
    RMSPROP = "rmsprop"


class TrainingConfig(BaseModel):
    optimizer: Optimizer
    learning_rate: Annotated[float, Gt(1e-5), Lt(1.0)]
    hidden_units: Annotated[int, Ge(32), Le(256)]


metadata = derive_optuna_metadata(
    TrainingConfig,
    log_scale_fields={"learning_rate"},
    categorical_field_weights={"optimizer": [0.5, 0.3, 0.2]},
)
attach_optuna_metadata(TrainingConfig, metadata)
```

`metadata` now contains Optuna-compatible distributions and the model fields
carry the same data inside `json_schema_extra` for downstream consumers.

## CLI

The package ships with a tiny demo CLI for smoke-testing constrained models:

```bash
uv run -m pydantic_optuna_bridge --help
uv run -m pydantic_optuna_bridge
```

## Development

```bash
uv run pytest
uv build
```

Pull requests and suggestions are welcome.
