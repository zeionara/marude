from enum import Enum


class Extension(Enum):
    MP3 = 'mp3'
    WAV = 'wav'
    TXT = 'txt'
    M4B = 'm4b'


EXTENSION_SEP = '.'


def separate_extension(path: str):
    if path is None:
        return None

    return tuple(component[::-1] for component in path[::-1].split(EXTENSION_SEP, maxsplit = 1)[::-1])


def drop_extension(path: str):
    if (components := separate_extension(path)) is None:
        return None

    return components[0]


def has_extension(path: str, extension: Extension):
    if (components := separate_extension(path)) is None:
        return None

    return components[1] == extension.value


def add_extension(path: str, extension: Extension):
    return f'{path}{EXTENSION_SEP}{extension.value}'
