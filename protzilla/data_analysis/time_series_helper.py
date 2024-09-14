from datetime import datetime

def convert_time_to_hours(time_str):
    """
    Convert a string time to the number of hours since midnight.
    :param time_str: The time string to convert in format '%H:%M:%S'

    :return: Number of hours since midnight as a float
    """

    """
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    hours_since_midnight = time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600
    """
    return time_str