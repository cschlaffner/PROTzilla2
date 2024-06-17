import protzilla.constants.colors as colorss


def customise(colors: str) -> dict:
    colorway = colors
    print("************")
    print(colors)
    colorss.get_color_sequence(colorway)
    return {'colors': colorway}

# todo: needs to be made shorter

# def saveColorways(colors: dict):
