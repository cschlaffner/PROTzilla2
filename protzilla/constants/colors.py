PLOT_COLOR_SEQUENCE = [
    "#4A536A",
    "#CE5A5A",
    "#87A8B9",
    "#8E3325",
    "#E2A46D",
]
"""List of colors to use in plots."""

PLOT_PRIMARY_COLOR = PLOT_COLOR_SEQUENCE[0]
"""First color in list. Conventionally used for visualizing outliers."""

PLOT_SECONDARY_COLOR = PLOT_COLOR_SEQUENCE[1]
"""Second color in list."""


def interpolate_color(color_a, color_b, t):
    """
    Interpolate between two RGB color strings based on a float t between 0 and 1.

    Args:
        color_a (str): RGB color string in the format "#RRGGBB".
        color_b (str): RGB color string in the format "#RRGGBB".
        t (float): A float between 0 and 1 representing the interpolation factor.

    Returns:
        str: Interpolated color as an RGB string in the format "#RRGGBB".
    """
    if not (0 <= t <= 1):
        raise ValueError("Interpolation factor t must be between 0 and 1")

    # Convert hex color strings to RGB tuples
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Convert RGB tuples back to hex color strings
    def rgb_to_hex(rgb):
        return f"#{''.join(f'{c:02x}' for c in rgb)}"

    rgb_a = hex_to_rgb(color_a)
    rgb_b = hex_to_rgb(color_b)

    # Interpolate each color channel
    interpolated_rgb = tuple(int(a + (b - a) * t) for a, b in zip(rgb_a, rgb_b))

    return rgb_to_hex(interpolated_rgb)
