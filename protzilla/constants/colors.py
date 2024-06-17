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

def get_color_from_run(steps: StepManager):
    global PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
    if steps.customising is not None:
        if steps.customising.colors is not None:
            if steps.customising.colors == "protan":
                PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = PROTAN_DISCRETE_COLOR_SEQUENCE
            elif steps.customising.colors == "deutan":
                PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = DEUTAN_DISCRETE_COLOR_SEQUENCE
            elif steps.customising.colors == "tritan":
                PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = TRITAN_DISCRETE_COLOR_SEQUENCE
            elif steps.customising.colors == "monochromatic":
                PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE
            else:
                PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = PROTZILLA_DISCRETE_COLOR_SEQUENCE
            return PROTZILLA_DISCRETE_COLOR_SEQUENCE
    else:
        return PROTZILLA_DISCRETE_COLOR_SEQUENCE
#maybe no return value needed
#put into dictionary

def get_color_sequence(colors: str):
    global PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
    if colors == "protan":
        PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = PROTAN_DISCRETE_COLOR_SEQUENCE
    elif colors == "deutan":
        PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = DEUTAN_DISCRETE_COLOR_SEQUENCE
    elif colors == "tritan":
        PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = TRITAN_DISCRETE_COLOR_SEQUENCE
    elif colors == "monochromatic":
        PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE
    else:
        return PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
