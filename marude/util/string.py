import re
from datetime import datetime

SPACE_SEQUENCE = re.compile(r'\s+')
DOT_SEQUENCE = re.compile(r'(?:\.\s+)+')

SINGLE_SPACE = ' '

DATE_TIME_FORMAT = "%d-%m-%Y %H:%M"


def normalize_spaces(string: str):
    return SPACE_SEQUENCE.sub(SINGLE_SPACE, string)


def normalize_dots(string: str):
    return DOT_SEQUENCE.sub(SINGLE_SPACE, string)


def from_date_time(date_time: datetime):
    return date_time.strftime(DATE_TIME_FORMAT)


def to_date_time(string: str):
    return datetime.strptime(string, DATE_TIME_FORMAT)
