# pydantic-optuna-bridge

Bridge constrained Pydantic models directly into Optuna search spaces. The
package extracts the metadata helpers originally built for
[`kaggle-map`](https://github.com/alexdong/kaggle-map) so that tightly scoped
hyperparameter schemas can be reused across projects.

## Installation

```bash
uv add pydantic-optuna-bridge
# or
pip install pydantic-optuna-bridge

# Optional CLI extras
uv add pydantic-optuna-bridge[cli]
```

## End-to-End Usage with Optuna

1. **Describe the search space in Pydantic.**
2. **Decorate the model to wire Optuna metadata and helpers.**
3. **Sample configurations inside an Optuna objective.**

Install Optuna alongside the bridge helpers:

```bash
uv add optuna
```

```python
from enum import Enum
from typing import Annotated

import optuna
from annotated_types import Ge, Gt, Le, Lt
from pydantic import BaseModel

from pydantic_optuna_bridge import optuna_config


class Optimizer(str, Enum):
    ADAM = "adam"
    SGD = "sgd"
    RMSPROP = "rmsprop"


@optuna_config(
    log_scale_fields={"learning_rate"},
    categorical_field_weights={"optimizer": [0.5, 0.3, 0.2]},
)
class TrainingConfig(BaseModel):
    optimizer: Optimizer
    learning_rate: Annotated[float, Gt(1e-5), Lt(1.0)]
    hidden_units: Annotated[int, Ge(32), Le(256)]

def objective(trial: optuna.trial.Trial) -> float:
    config = TrainingConfig.from_optuna_trial(trial)

    # Replace with real training logic, keeping a toy signal for documentation.
    score = (
        0.1 if config.optimizer == Optimizer.ADAM else 0.2
    ) + 0.05 * abs(config.learning_rate - 1e-2) + config.hidden_units / 1_024
    return score


study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=5)
print(study.best_params)
```

Optuna now drives the search space defined by the Pydantic model. Because the
decorator attaches metadata to `json_schema_extra`, downstream tools can inspect
the schema without re-deriving it:

```python
schema_payload = {
    name: field.json_schema_extra["optuna"]
    for name, field in TrainingConfig.model_fields.items()
}
assert schema_payload == TrainingConfig.optuna_metadata()
```

## CLI Demo

The optional CLI showcases the metadata derivation and prints a formatted table
for inspection:

```bash
uv run -m pydantic_optuna_bridge --help
uv run -m pydantic_optuna_bridge
```

## Development

```bash
uv run pytest
uv build
```

Issues and pull requests are welcome.
