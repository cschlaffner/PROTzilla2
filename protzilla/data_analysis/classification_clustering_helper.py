from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline


def update_raw_evaluation_data(results, params, train_scores, val_scores):
    for param_name, param_value in params.items():
        results |= {f"param_{param_name}": param_value}
    results["mean_train_score"].append(np.mean(train_scores))
    results["std_train_score"].append(np.std(train_scores))
    results["mean_test_score"].append(np.mean(val_scores))
    results["std_test_score"].append(np.std(val_scores))
    return results


@dataclass
class GridSearchManual:
    model: Pipeline
    param_grid: dict
    train_val_split: tuple = None
    results: dict = field(
        default_factory=lambda: {
            "mean_train_score": [],
            "mean_test_score": [],
            "std_train_score": [],
            "std_test_score": [],
        }
    )

    def fit(self, train_val_split):
        self.train_val_split = train_val_split
        X_train, X_val, y_train, y_val = self.train_val_split
        # Iterate over the parameter grid
        for params in ParameterGrid(self.param_grid):
            model = self.model.set_params(**params)
            model.fit(X_train, y_train)
            train_scores = model.score(X_train, y_train)
            val_scores = model.score(X_val, y_val)

            # Store the results for the current parameter combination
            self.results = update_raw_evaluation_data(
                self.results, params, train_scores, val_scores
            )

        return self.model
