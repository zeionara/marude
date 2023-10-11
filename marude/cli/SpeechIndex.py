from os import walk, path
from pathlib import Path
from collections import namedtuple

Key = namedtuple('AnekId', field_names = ('source', 'id'))
Location = namedtuple('Location', field_names = ('path', 'file'))


class SpeechIndex:
    def __init__(self, root: str):
        self.root = root

        index = {}

        n_files = 0

        for directory, _, files in walk(root):
            for file in files:
                components = Path(file).stem.split('.')

                assert len(components) == 2, f'Incorrect file name {file}'

                index[Key(source = components[1], id = int(components[0]))] = Location(path = path.join(directory, file), file = file)

                n_files += 1

        print(f'Indexed {n_files} files')

        self._index = index

    def get(self, source: str, id_: int):
        return self._index[Key(source = source, id = id_)]
