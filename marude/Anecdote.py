from os import environ as env
from urllib.parse import urlencode
from dataclasses import dataclass
from datetime import datetime

from requests import post
from tasty import pipe
from pandas import DataFrame

from .util.string import normalize_spaces, normalize_dots


MARUDE_VK_API_KEY = env['MARUDE_VK_API_KEY']
VK_API_VERSION = '5.131'


@dataclass
class Anecdote:
    text: str
    date_time: datetime
    id_: int
    n_likes: int
    n_views: int

    def describe(self, sep: str = '\t'):
        return f'{self.id_}{sep}{self.date_time.strftime("%d-%m-%Y %H:%M")}{sep}{self.text}{sep}{self.n_likes}{sep}{self.n_views}'

    @property
    def as_dict(self):
        return {
            'text': self.text,
            'date-time': self.date_time.strftime("%d-%m-%Y %H:%M"),
            'id': self.id_,
            'n-likes': self.n_likes,
            'n-views': self.n_views
        }


class AnecdoteCollection:
    def __init__(self, items: list[Anecdote]):
        self.items = items

    @classmethod
    def from_vk(cls, domain: str, min_date_time: datetime = None, batch_size: int = 100, timeout: int = 10):
        offset = 0
        items = []

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

                    if len(new_items) == 0:
                        break

                    items.extend(
                        new_item_objects := [
                            Anecdote(
                                item['text'] | pipe | normalize_spaces | pipe | normalize_dots,
                                datetime.fromtimestamp(item['date']),
                                item['id'],
                                item['likes']['count'],
                                item['views']['count']
                            )
                            for item in new_items
                            if item.get('is_pinned') != 1
                        ]
                    )

                    offset += len(new_items)

                    print(f'Handled {offset}/{response_["count"]} items (+{len(new_item_objects)}/{len(new_items)})')
                case _:
                    raise ValueError(f'Incorrect response code: {status_code}')

        return AnecdoteCollection(items = items)

    @property
    def as_df(self):
        return DataFrame(item.as_dict for item in self.items)
