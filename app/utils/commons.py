import csv
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


def list_dict_to_csv(list_dict, filename='list_dict.csv'):
    keys = list_dict[0].keys()
    with open(filename, 'w', newline='') as output_file:
    # with open(filename, 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_dict)
