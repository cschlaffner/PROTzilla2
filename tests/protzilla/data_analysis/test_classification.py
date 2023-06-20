import pandas as pd
import pytest

from protzilla.data_analysis.model_evaluation import evaluate_classification_model
from tests.conftest import open_graph_from_base64
from protzilla.data_analysis.classification import random_forest
from protzilla.data_analysis.model_evaluation_plots import (
    precision_recall_curve_plot,
    roc_curve_plot,
)


@pytest.fixture
def classification_df():
    classification_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 19],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
        ["Sample8", "Protein1", "Gene1", 42],
        ["Sample8", "Protein2", "Gene1", 33],
        ["Sample8", "Protein3", "Gene1", 3],
        ["Sample9", "Protein1", "Gene1", 19],
        ["Sample9", "Protein2", "Gene1", 1],
        ["Sample9", "Protein3", "Gene1", 4],
    )

    classification_df = pd.DataFrame(
        data=classification_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return classification_df


@pytest.fixture
def meta_df():
    meta_list = (
        ["Sample1", "AD"],
        ["Sample2", "AD"],
        ["Sample3", "AD"],
        ["Sample4", "CTR"],
        ["Sample5", "CTR"],
        ["Sample6", "CTR"],
        ["Sample7", "CTR"],
        ["Sample8", "AD"],
        ["Sample9", "CTR"],
    )
    meta_df = pd.DataFrame(
        data=meta_list,
        columns=["Sample", "Group"],
    )

    return meta_df


@pytest.fixture
def meta_numeric_df():
    meta_list = (
        ["Sample1", "1"],
        ["Sample2", "1"],
        ["Sample3", "1"],
        ["Sample4", "0"],
        ["Sample5", "0"],
        ["Sample6", "0"],
        ["Sample7", "0"],
        ["Sample8", "1"],
        ["Sample9", "0"],
    )
    meta_df = pd.DataFrame(
        data=meta_list,
        columns=["Sample", "Group"],
    )

    return meta_df


@pytest.fixture
def random_forest_out(
    classification_df,
    meta_df,
    validation_strategy="K-Fold",
    model_selection="Grid search",
):
    return random_forest(
        classification_df,
        meta_df,
        "Group",
        n_estimators=3,
        test_validate_split=0.20,
        model_selection=model_selection,
        validation_strategy=validation_strategy,
        random_state=42,
    )


@pytest.mark.parametrize(
    "validation_strategy,model_selection",
    [
        ("Manual", "Manual"),
        ("K-Fold", "Manual"),
        ("K-Fold", "Grid search"),
        ("K-Fold", "Randomized search"),
    ],
)
def test_random_forest_score(random_forest_out, validation_strategy, model_selection):
    model_evaluation_df = random_forest_out["model_evaluation_df"]
    assert (
        model_evaluation_df["mean_test_accuracy"].values[0] >= 0.8
    ), f"Failed with validation strategy {validation_strategy} and model selection strategy {model_selection}"


def test_model_evaluation_plots(show_figures, random_forest_out):
    recall_curve_base64 = precision_recall_curve_plot(
        random_forest_out["model"],
        random_forest_out["X_test_df"],
        random_forest_out["y_test_df"],
    )
    roc_curve_base64 = roc_curve_plot(
        random_forest_out["model"],
        random_forest_out["X_test_df"],
        random_forest_out["y_test_df"],
    )

    if show_figures:
        open_graph_from_base64(recall_curve_base64[0])
        open_graph_from_base64(roc_curve_base64[0])


def test_evaluate_classification_model(show_figures, random_forest_out):
    evaluation_out = evaluate_classification_model(
        random_forest_out["model"],
        random_forest_out["X_test_df"],
        random_forest_out["y_test_df"],
        ["accuracy", "precision", "recall", "matthews_corrcoef"],
    )
    scores_df = evaluation_out["scores_df"]
    assert (scores_df["Score"] == 1).all()
