from os import makedirs, path as os_path, remove
from multiprocessing import Queue, Process

from click import group, argument, option, Choice
from tasty import pipe

from .util.path import drop_extension, add_extension, Extension
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


def _recognize_text(queue: Queue, result_path: str, result_path_punctuated: str):
    client = CloudVoiceClient()

    try:
        remove(result_path)
    except:
        pass

    try:
        remove(result_path_punctuated)
    except:
        pass

    while True:
        message = queue.get()

        for text in client.asr(path := message.path):

            with open(result_path, 'a', encoding = 'utf-8') as file:
                file.write(text.text + '\n')

            with open(result_path_punctuated, 'a', encoding = 'utf-8') as file:
                file.write(text.text_punctuated + '\n')

            print(f'Recognized text from file {path}')

        if message.last:
            break


@main.command()
@argument('input_path', type = str)
@argument('output_path', type = str, required = False)
@option('--shortest-silence', '-ss', type = float, default = 0.5)
@option('--shortest-part', '-sp', type = float, default = 60.0)
@option('--longest-part', '-sp', type = float, default = 100.0)
def asr(input_path: str, output_path: str, shortest_silence: float, shortest_part: float, longest_part: float):

    if output_path is None:
        makedirs(output_path := input_path | pipe | drop_extension, exist_ok = True)

    queue = Queue()

    producer = Process(target = split_, args = (input_path, output_path, shortest_silence, longest_part, shortest_part, queue))
    producer.start()

    consumer = Process(
        target = _recognize_text,
        args = (
            queue,
            add_extension(os_path.join(output_path, 'text'), Extension.TXT),
            add_extension(os_path.join(output_path, 'text-punctuated'), Extension.TXT),
        )
    )
    consumer.start()


@main.command()
@argument('input-path', type = str)
@argument('output-path', type = str, required = False)
@option('--shortest-silence', '-ss', type = float, default = 0.5)
@option('--shortest-part', '-sp', type = float, default = 60.0)
@option('--longest-part', '-lp', type = float, default = 100.0)
def split(input_path: str, output_path: str, shortest_silence: float, shortest_part: float, longest_part: float):
    if output_path is None:
        makedirs(output_path := input_path | pipe | drop_extension, exist_ok = True)

    split_(input_path, output_path, shortest_silence, longest_part, shortest_part)


if __name__ == '__main__':
    main()
