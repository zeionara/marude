from requests import post
from enum import Enum


class Voice(Enum):
    KATHERINE = 'katherine'
    PAVEL = 'pavel'
    MARIA = 'maria'


class CloudVoiceClient:
    max_text_length = 1024

    def __init__(self, voice: Voice = Voice.KATHERINE):
        self.voice = voice

    def tts(self, text: str) -> bytes:
        assert len(text) <= self.max_text_length, f'Text must be at most {self.max_text_length} characters long'

        text_encoded = f'"{text}"'.encode("utf-8")

        response = post(
            f'https://mcs.mail.ru/tts_demo?encoder=mp3&tempo=1&model_name={self.voice.value}',
            data = text_encoded,
            timeout = 10  # seconds
        )

        match (status_code := response.status_code):
            case 200:
                return response.content
            case _:
                raise ValueError(f'Unacceptable response status code: {status_code}')
