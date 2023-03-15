import re

SPACE_SEQUENCE = re.compile(r'\s+')
DOT_SEQUENCE = re.compile(r'(?:\.\s+)+')

SINGLE_SPACE = ' '


def normalize_spaces(string: str):
    return SPACE_SEQUENCE.sub(SINGLE_SPACE, string)


def normalize_dots(string: str):
    return DOT_SEQUENCE.sub(SINGLE_SPACE, string)
