import protzilla.constants.colors as color_constants
import protzilla.constants.text as text_constants


def color_choice_method(colors: str, custom_colors: str) -> dict:
    if colors != "custom":
        color_constants.get_color_sequence(colors)
        color_constants.get_continuous_color_sequence(colors)
        color_constants.get_diverging_color_sequence(colors)
    else:
        color_constants.set_custom_sequence(custom_colors)
    return {'colors': colors, 'custom_color_value': custom_colors}


def enhanced_reading_method(enhanced_reading: bool) -> dict:
    text_constants.get_text_parameters(enhanced_reading)
    return {'enhanced_reading': enhanced_reading}
