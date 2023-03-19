from __future__ import annotations

from os import environ as env
from urllib.parse import urlencode
from dataclasses import dataclass
from datetime import datetime

from requests import post
from tasty import pipe
from pandas import DataFrame, read_csv

from .util.string import normalize_spaces, normalize_dots, from_date_time, to_date_time


MARUDE_VK_API_KEY = env['MARUDE_VK_API_KEY']
VK_API_VERSION = '5.131'


@dataclass
class Anecdote:
    text: str
    published: datetime
    id_: int
    n_likes: int
    n_views: int
    accessed: datetime
    _is_pinned: bool = False

    def describe(self, sep: str = '\t'):
        return f'{self.id_}{sep}{from_date_time(self.published)}{sep}{self.text}{sep}{self.n_likes}{sep}{self.n_views}{sep}{from_date_time(self.accessed)}'

    @property
    def as_dict(self):
        return {
            'text': self.text,
            'published': from_date_time(self.published),
            'id': self.id_,
            'n-likes': self.n_likes,
            'n-views': self.n_views,
            'accessed': from_date_time(self.accessed)
        }

    @classmethod
    def from_dict(cls, values: dict):
        return Anecdote(
            values['text'],
            to_date_time(values['published']),
            values['id'],
            values['n-likes'],
            values['n-views'],
            to_date_time(values['accessed'])
        )


class AnecdoteCollection:
    def __init__(self, items: list[Anecdote], ids: set[int]):
        self.items = items
        self.ids = ids

    @classmethod
    def from_vk(cls, domain: str, accessed: datetime, batch_size: int = 100, timeout: int = 10, after: AnecdoteCollection = None):
        offset = 0
        items = []
        ids = set()

        is_last_batch = None if after is None else False

        # for _ in range(2):
        while True:
            response = post(
                'https://api.vk.com/method/wall.get',
                data = urlencode(
                    {
                        'access_token': MARUDE_VK_API_KEY,
                        'domain': domain,
                        'offset': offset,
                        'count': batch_size,
                        'v': VK_API_VERSION
                    }
                ),
                timeout = timeout
            )

            match (status_code := response.status_code):
                case 200:
                    body = response.json()
                    new_items = (response_ := body['response'])['items']

                    if (n_new_items := len(new_items)) == 0:
                        break

                    offset += n_new_items

                    n_new_item_objects = 0

                    for item in new_items:
                        # if item.get('is_pinned') != 1:
                        try:
                            views = item.get('views')
                            item = Anecdote(
                                item['text'] | pipe | normalize_spaces | pipe | normalize_dots,
                                datetime.fromtimestamp(item['date']),
                                item_id := item['id'],
                                item['likes']['count'],
                                None if views is None else views.get('count'),
                                accessed,
                                item.get('is_pinned') == 1
                            )
                        except KeyError as e:
                            raise ValueError(f'Cannot decode post {item}') from e

                        if after is not None and item in after:
                            if item._is_pinned:
                                continue
                            is_last_batch = True
                            break

                        n_new_item_objects += 1
                        items.append(item)
                        ids.add(item_id)

                    print(f'Handled {offset}/{response_["count"]} items (+{n_new_item_objects}/{n_new_items})')

                    if is_last_batch is True:
                        break
                case _:
                    raise ValueError(f'Incorrect response code: {status_code}')

        return AnecdoteCollection(items = items, ids = ids)

    @classmethod
    def from_file(cls, path: str):
        df = read_csv(path, sep = '\t')

        items = []
        ids = set()

        for item in df.to_dict('records'):
            items.append(item := Anecdote.from_dict(item))
            ids.add(item.id_)

        return AnecdoteCollection(items, ids)

    def __contains__(self, item: Anecdote):
        return item.id_ in self.ids

    def __getitem__(self, index: int):
        return self.items[index]

    @property
    def as_df(self):
        return DataFrame(item.as_dict for item in self.items)
