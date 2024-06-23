from protzilla.steps import StepManager

PROTZILLA_DISCRETE_COLOR_SEQUENCE = [
    "#4A536A",
    "#87A8B9",
    "#CE5A5A",
    "#8E3325",
    "#E2A46D",
]

PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = [
    "#4A536A",
    "#CE5A5A"
]

PROTAN_DISCRETE_COLOR_SEQUENCE = [
    "#3673c4",
    "#e3a22a",
]
# justify how colors come about
DEUTAN_DISCRETE_COLOR_SEQUENCE = [
    "#3673c4",
    "#000000",
]

TRITAN_DISCRETE_COLOR_SEQUENCE = [
    "#3673c4",
    "#f48e9b"
]

MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE = [
    "#3b3b3b",
    "#D3D3D3"
]


def get_color_sequence(colors: str):
    color_sequences = {
        "protan": PROTAN_DISCRETE_COLOR_SEQUENCE,
        "deutan": DEUTAN_DISCRETE_COLOR_SEQUENCE,
        "tritan": TRITAN_DISCRETE_COLOR_SEQUENCE,
        "monochromatic": MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE
    }
    global PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE

    if colors in color_sequences:
        PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = color_sequences[colors]


