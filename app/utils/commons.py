from datetime import datetime


def get_current_datetime(str_format="%Y%m%d_%H%M%S") -> str:
    now = datetime.now()
    str_current_datetime = now.strftime(str_format)
    return str_current_datetime


def parse_year_from_username(username: str) -> int:
    code = username[4:6] if len(username) > 6 else ""
    current_year = get_current_datetime("%Y")
    current_year_code = current_year[:2]
    year = int(current_year_code + code)
    return year
