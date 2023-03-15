import re
from datetime import datetime
from nltk.tokenize import sent_tokenize

SPACE_SEQUENCE = re.compile(r'\s+')
DOT_SEQUENCE = re.compile(r'(?:\.\s+)+')
SENTENCE_IMPLICIT_BOUNDARY = re.compile(r'([a-zа-яё]) ([А-ЯA-ZЁ](?:\s+)?[a-zа-яё])')

SINGLE_SPACE = ' '

DATE_TIME_FORMAT = "%d-%m-%Y %H:%M"


def normalize_spaces(string: str):
    return SPACE_SEQUENCE.sub(SINGLE_SPACE, string)


def add_sentence_terminators(string: str):
    return SENTENCE_IMPLICIT_BOUNDARY.sub(r'\g<1>. \g<2>', string)


def normalize_dots(string: str):
    return DOT_SEQUENCE.sub(SINGLE_SPACE, string)


def from_date_time(date_time: datetime):
    return date_time.strftime(DATE_TIME_FORMAT)


def to_date_time(string: str):
    return datetime.strptime(string, DATE_TIME_FORMAT)


def segment(string: str, max_length: int = 1024):
    segments = []

    current_segment = []

    def append_current_segment():
        nonlocal current_segment

        if len(current_segment) > 0:
            segments.append(' '.join(current_segment))
            current_segment = []

    for sentence in sent_tokenize(string):
        while len(sentence) > max_length:
            append_current_segment()
            segments.append(sentence[:max_length])
            sentence = sentence[max_length:]

        if sum(len(segment_part) for segment_part in current_segment) + len(current_segment) - 1 + len(sentence) > max_length:
            append_current_segment()

        current_segment.append(sentence)

    append_current_segment()

    return tuple(segments)
