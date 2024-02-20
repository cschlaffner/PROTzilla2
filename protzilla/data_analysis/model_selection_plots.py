import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from sklearn.model_selection import LearningCurveDisplay

from protzilla.utilities import fig_to_base64, remove_underscore_and_capitalize


def learning_curve_plot(
    train_sizes,
    train_scores,
    test_scores,
    score_name,
    model_function,
    initial_coef_model_function,
    plot_title,
):
    # learning curve with training and validation score
    display = LearningCurveDisplay(
        train_sizes=train_sizes,
        train_scores=np.array(train_scores),
        test_scores=np.array(test_scores),
        score_name=score_name,
    )
    display.plot(
        score_type="both",
        line_kw={"marker": "o"},
    )
    # set legend names for each curve
    legend = plt.legend()
    plt.title(plot_title)
    plt.ylim(0.35, 1.05)
    legend_labels = [f"Training {score_name}", f"Test {score_name}"]
    for text, label in zip(legend.get_texts(), legend_labels):
        text.set_text(label)

    # find flattening point in learning curve

    test_scores_mean = np.array(test_scores).mean(axis=1)
    params, _ = curve_fit(
        model_functions[model_function],
        train_sizes,
        test_scores_mean,
        p0=initial_coef_model_function,
    )

    x_fit = np.linspace(min(train_sizes), max(train_sizes), 100)
    curve_values = model_functions[model_function](x_fit, *params)

    if model_function == "cubic_function":
        diff = np.diff(curve_values)
        mask = x_fit > 60
        filtered_diff = diff[mask[:-1]]
        filtered_x_fit = x_fit[mask]
        flattening_point_idx = np.argmax(filtered_diff < np.mean(filtered_diff))
        flattening_point = filtered_x_fit[flattening_point_idx]
    else:
        diff = np.diff(curve_values)
        flattening_point_idx = np.argmax(diff < np.mean(diff))
        flattening_point = x_fit[flattening_point_idx]

    plt.figure()
    plt.plot(train_sizes, test_scores_mean, "o-", label=f"Test {score_name}")
    plt.plot(x_fit, curve_values, "r-", label="Fitted Curve")
    plt.axvline(
        flattening_point,
        ls="--",
        color="gray",
        label="Minimum Viable Sample Size",
    )
    plt.xlabel("Training Set Size")
    plt.ylabel(score_name)
    plt.ylim(0.35, 1.05)
    plt.title(plot_title)
    plt.legend()
    display_flat = plt.gcf()

    return [fig_to_base64(display.figure_), fig_to_base64(display_flat)]


model_functions = {
    "sigmoid": lambda x, a, b, c: a / (1 + np.exp(-b * (x - c))),
    "exponential": lambda x, a, b, c: a * np.exp(b * x) + c,
    "cubic_function": lambda x, a, b, c, d: a * x**3 + b * x**2 + c * x + d,
}
