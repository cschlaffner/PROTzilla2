import protzilla.constants.text as text_constants


def style_text(text: str, letter_spacing: float, word_spacing: float) -> str:
    """
    Function to style text with letter spacing and word spacing.

    :param text: The text to be styled.
    :param letter_spacing: The amount of letter spacing.
    :param word_spacing: The amount of word spacing.
    :return: HTML formatted string with specified letter and word spacing.
    """
    return f'<span style="letter-spacing:{letter_spacing}pt;word-spacing:{word_spacing}pt;">{text}</span>'


def get_text_parameters():
    """
        Retrieves text parameters from PROTZILLA_TEXT_PARAMETERS.
    """
    add_font_size = text_constants.PROTZILLA_TEXT_PARAMETERS["add_font_size"]
    add_letter_spacing = text_constants.PROTZILLA_TEXT_PARAMETERS["add_letter_spacing"]
    add_word_spacing = text_constants.PROTZILLA_TEXT_PARAMETERS["add_word_spacing"]
    return add_font_size, add_letter_spacing, add_word_spacing


def get_enhanced_reading_value():
    """
        Retrieves enhanced reading value from PROTZILLA_TEXT_PARAMETERS.
    """
    return text_constants.PROTZILLA_TEXT_PARAMETERS["enhanced_reading"]
