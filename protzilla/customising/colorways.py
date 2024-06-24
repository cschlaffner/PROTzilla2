import protzilla.constants.colors as color_constants


def customise(colors: str, custom_colors: str) -> dict:
    if colors != "custom":
        color_constants.get_color_sequence(colors)
    else:
        color_constants.set_custom_sequence(custom_colors)
    return {'colors': colors, 'custom_color_value': custom_colors}


