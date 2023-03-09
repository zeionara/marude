from click import group, argument, option, Choice
from tasty import pipe

from .CloudVoiceClient import CloudVoiceClient, Voice


@group()
def main():
    pass


@main.command()
@argument('text', type = str)
@option('--path', '-p', type = str, default = 'assets/message.mp3')
@option('--model', '-m', type = Choice([voice.value for voice in Voice]), default = 'katherine')
def tts(text: str, path: str, model: str):
    with open(path, 'wb') as file:
        _ = text | pipe | CloudVoiceClient(voice = Voice(model)).tts | pipe | file.write


if __name__ == '__main__':
    main()
