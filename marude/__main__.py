from os import makedirs

from click import group, argument, option, Choice
from tasty import pipe

from .util.path import drop_extension
from .util.audio import split as split_

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


@main.command()
@argument('input_path', type = str)
@argument('output_path', type = str, required = False)
@option('--shortest-silence', '-ss', type = float, default = 1.0)
@option('--shortest-part', '-sp', type = float, default = 60.0)
@option('--longest-part', '-sp', type = float, default = 100.0)
def split(input_path: str, output_path: str, shortest_silence: float, shortest_part: float, longest_part: float):
    print(CloudVoiceClient().asr('assets/real-colonel/00.wav'))

    # if output_path is None:
    #     makedirs(output_path := input_path | pipe | drop_extension, exist_ok = True)

    # split_(input_path, output_path, shortest_silence, longest_part, shortest_part)


if __name__ == '__main__':
    main()
