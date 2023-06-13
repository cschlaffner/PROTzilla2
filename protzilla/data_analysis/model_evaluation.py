import pandas as pd

from protzilla.data_analysis.classification_helper import (
    evaluate_with_scoring,
    encode_labels,
)


def evaluate_classification_model(model, input_test_df, labels_test_df, scoring):
    input_test_df = input_test_df.set_index("Sample")
    label_encoder, y_test_encoded = encode_labels(
        input_test_df, labels_test_df, "Label"
    )

    y_pred = model.predict(input_test_df)
    scores = evaluate_with_scoring(scoring, y_test_encoded, y_pred)

    scores_df = pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
    scores_df = scores_df.reset_index().rename(columns={"index": "Metric"})
    return dict(scores_df=scores_df)
