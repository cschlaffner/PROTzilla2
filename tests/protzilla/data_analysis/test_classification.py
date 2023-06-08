import pandas as pd
import pytest

from protzilla.data_analysis.classification import random_forest


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
    )
    meta_df = pd.DataFrame(
        data=meta_list,
        columns=["Sample", "Group"],
    )

    return meta_df


@pytest.fixture
def meta_numeric_df():
    meta_list = (
        ["Sample1", "0"],
        ["Sample2", "0"],
        ["Sample3", "0"],
        ["Sample4", "1"],
        ["Sample5", "1"],
        ["Sample6", "1"],
        ["Sample7", "1"],
    )
    meta_df = pd.DataFrame(
        data=meta_list,
        columns=["Sample", "Group"],
    )

    return meta_df


@pytest.fixture
def random_forest_out(classification_df, meta_df, validation_strategy, model_selection):
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
        ("Manual", "Grid search"),
        ("K-Fold", "Manual"),
        ("K-Fold", "Grid search"),
        ("K-Fold", "Randomized search"),
    ],
)
def test_random_forest_score(random_forest_out, validation_strategy, model_selection):
    model_evaluation_df = random_forest_out["model_evaluation_df"]
    assert (
        model_evaluation_df["mean_test_score"].values[0] > 0.8
    ), f"Failed with validation strategy {validation_strategy} and model selection strategy {model_selection}"
