STANDARD_PROTZILLA_TEXT_PARAMETERS = {
    "enhanced_reading": False,
    "add_font_size": 0,
    "add_letter_spacing": 0,
    "add_word_spacing": 0
}

PROTZILLA_TEXT_PARAMETERS = STANDARD_PROTZILLA_TEXT_PARAMETERS.copy()

PROTZILLA_ENHANCED_READING_TEXT_PARAMETERS = {
    "enhanced_reading": True,
    "add_font_size": 2,
    "add_letter_spacing": 2.5,
    "add_word_spacing": 8.75
}


def get_text_parameters(enhanced_reading: bool):
    global PROTZILLA_TEXT_PARAMETERS
    if enhanced_reading:
        PROTZILLA_TEXT_PARAMETERS = PROTZILLA_ENHANCED_READING_TEXT_PARAMETERS
    else:
        PROTZILLA_TEXT_PARAMETERS = STANDARD_PROTZILLA_TEXT_PARAMETERS

