from datetime import datetime


def get_current_datetime(str_format="%Y%m%d_%H%M%S") -> str:
    now = datetime.now()
    str_current_datetime = now.strftime(str_format)
    return str_current_datetime
