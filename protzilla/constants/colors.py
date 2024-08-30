import re
import matplotlib.pyplot as plt
import numpy as np

# Use for plots that require more than 6 colors or a continuous color scale with no neutral middle point
PROTZILLA_CONTINUOUS_COLOR_SEQUENCE = plt.get_cmap("plasma")
CVD_CONTINUOUS_COLOR_SEQUENCE = plt.get_cmap("cividis")

# Use for plots that require a neutral middle point e.g. heat maps
PROTZILLA_DIVERGING_COLOR_SEQUENCE = plt.get_cmap("Spectral")
CVD_DIVERGING_COLOR_SEQUENCE = plt.get_cmap("BrBG")

PROTZILLA_DISCRETE_COLOR_SEQUENCE = [
    "#4A536A",  # blue
    "#CE5A5A",  # red
    "#87A8B9",  # light blue
    "#A7A1B2",  # grey
    "#F1A765",  # orange
    "#8E3F25"   # dark red

     ]

PROTAN_DISCRETE_COLOR_SEQUENCE = [
    "#4A536A",  # blue
    "#daa217",  # yellow
    "#a8b3ef",  # light blue
    "#a1a5b2",  # grey
    "#0051a9",  # dark blue
    "#7D7800"   # dark yellow

]

DEUTAN_DISCRETE_COLOR_SEQUENCE = [
    "#4A536A",  # blue
    "#FF911E",  # yellow
    "#A4B6EF",  # light blue
    "#a1a5b2",  # grey
    "#0062a9",  # dark blue
    "#986400"  # dark yellow

]

TRITAN_DISCRETE_COLOR_SEQUENCE = [
    "#48565d",  # blue
    "#f48e9b",  # pink
    "#6C9AAF",  # light blue
    "#a1a5b2",  # grey
    "#22c6d5",  # turquoise
    "#8e3e42"   # dark pink
]

# This sequence shouldn't be used if the plot requires all six or more colors,
# without making modifications in the plot itself,
# as the colors are very similar to each other.
MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE = [
    "#929292",  # medium grey
    "#4C4C4C",  # dark grey
    "#949494",  # light grey
    "#C5C5C5",  # grey
    "#333333",  # black-ish
    "#000000"  # black

]

HIGH_CONTRAST_DISCRETE_COLOR_SEQUENCE = [
    "#2E3850",  # dark blue
    "#F13232",  # red
    "#5BBBEC",  # light blue
    "#ABABAF",  # grey
    "#FFC000",  # orange
    "#1767CE"  # blue
]


def get_color_sequence(colors: str):
    global PROTZILLA_DISCRETE_COLOR_SEQUENCE
    color_sequences = {
        "standard": PROTZILLA_DISCRETE_COLOR_SEQUENCE,
        "protan": PROTAN_DISCRETE_COLOR_SEQUENCE,
        "deutan": DEUTAN_DISCRETE_COLOR_SEQUENCE,
        "tritan": TRITAN_DISCRETE_COLOR_SEQUENCE,
        "monochromatic": MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE,
        "high_contrast": HIGH_CONTRAST_DISCRETE_COLOR_SEQUENCE
    }

    if colors in color_sequences:
        PROTZILLA_DISCRETE_COLOR_SEQUENCE = color_sequences[colors]


def get_continuous_color_sequence(colors: str):
    global PROTZILLA_CONTINUOUS_COLOR_SEQUENCE
    if colors in ["standard", "high_contrast"]:
        return
    else:
        PROTZILLA_CONTINUOUS_COLOR_SEQUENCE = CVD_CONTINUOUS_COLOR_SEQUENCE


def get_diverging_color_sequence(colors: str):
    global PROTZILLA_DIVERGING_COLOR_SEQUENCE
    if colors in ["standard", "high_contrast"]:
        return
    else:
        PROTZILLA_DIVERGING_COLOR_SEQUENCE = CVD_DIVERGING_COLOR_SEQUENCE


def set_custom_sequence(custom_color_sequence: str):
    global PROTZILLA_DISCRETE_COLOR_SEQUENCE

    if not (is_valid_hex_color_pair(custom_color_sequence)):
        raise ValueError("Invalid hex color pair")

    custom_color_list = custom_color_sequence.split(",")
    PROTZILLA_DISCRETE_COLOR_SEQUENCE = custom_color_list


def is_valid_hex_color_pair(s):
    hex_color_pattern = r'#[0-9a-fA-F]{6}'
    pattern = re.compile(f'^{hex_color_pattern}, {hex_color_pattern}$')
    return bool(pattern.match(s))
