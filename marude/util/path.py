from enum import Enum


class Extension(Enum):
    WAV = 'wav'
    TXT = 'txt'


EXTENSION_SEP = '.'


def drop_extension(path: str):
    if path is None:
        return None

    components = path[::-1].split(EXTENSION_SEP, maxsplit = 1)

    if len(components) == 1:
        return components[0]

    return components[1][::-1]


def add_extension(path: str, extension: Extension):
    return f'{path}{EXTENSION_SEP}{extension.value}'
