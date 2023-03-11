from enum import Enum
from os import path as path_
from dataclasses import dataclass

from requests import post, Response

from .util.audio.analysis import get_duration
from .util.collection import as_tuple

DEFAULT_TIMEOUT = 10  # seconds


class Voice(Enum):
    KATHERINE = 'katherine'
    PAVEL = 'pavel'
    MARIA = 'maria'


@dataclass
class RecognizedText:
    text: str
    text_punctuated: str

    @classmethod
    @as_tuple
    def from_response_body(cls, body: dict):
        for text in body['result']['texts']:
            yield RecognizedText(text['text'], text['punctuated_text'])


class CloudVoiceClient:
    max_text_length = 1024
    max_speech_duration = 120  # seconds
    max_speech_file_size = 20  # mbytes

    def __init__(self, voice: Voice = Voice.KATHERINE, timeout = DEFAULT_TIMEOUT):
        self.voice = voice
        self.timeout = timeout

    def _handle_errors(self, response: Response, post_process: callable):
        match (status_code := response.status_code):
            case 200:
                return post_process(response)
            case _:
                raise ValueError(f'Unacceptable response status code: {status_code}')

    def tts(self, text: str) -> bytes:
        assert len(text) <= self.max_text_length, f'Text must be at most {self.max_text_length} characters long'

        text_encoded = f'"{text}"'.encode("utf-8")

        response = post(
            f'https://mcs.mail.ru/tts_demo?encoder=mp3&tempo=1&model_name={self.voice.value}',
            data = text_encoded,
            timeout = self.timeout
        )

        return self._handle_errors(response, lambda response: response.content)

    def asr(self, path: str) -> tuple[RecognizedText]:
        assert (duration := get_duration(path)) < self.max_speech_duration, f'The audiofile is too long: {duration} > {self.max_speech_duration}'
        assert (size := path_.getsize(path) / 1e+6) < self.max_speech_file_size, f'The audiofile is too big: {size} > {self.max_speech_file_size}'

        # return (RecognizedText('foo', 'bar'), )

        with open(path, 'rb') as file:
            data = file.read()

        response = post(
            'https://mcs.mail.ru/asr_demo',
            data=data,
            timeout = self.timeout,
            headers = {
                'Content-type': 'audio/wav'
            }
        )

        return self._handle_errors(response, lambda response: RecognizedText.from_response_body(response.json()))
