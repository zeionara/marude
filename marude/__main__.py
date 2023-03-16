from io import BytesIO
from os import makedirs, path as os_path, remove
from multiprocessing import Queue, Process
from datetime import datetime

from click import group, argument, option, Choice
from tasty import pipe
from pydub import AudioSegment

from .util.path import drop_extension, add_extension, Extension
from .util.audio import split as split_
from .util.string import segment, add_sentence_terminators

from .CloudVoiceClient import CloudVoiceClient, Voice
from .Anecdote import AnecdoteCollection


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


@main.command()
@argument('output-path', type = str)
@option('--batch-size', '-b', type = int, default = 100)
@option('--after', '-a', type = str, default = None)
def fetch_anecdotes(output_path: str, batch_size: int, after: str):
    if after is None:
        AnecdoteCollection.from_vk('anekdotikategoriib', datetime.now(), batch_size = batch_size).as_df.to_csv(output_path, sep = '\t', index = False)
    else:
        anecdotes = AnecdoteCollection.from_file(after)
        AnecdoteCollection.from_vk('anekdotikategoriib', datetime.now(), batch_size = batch_size, after = anecdotes).as_df.to_csv(output_path, sep = '\t', index = False)


@main.command()
@argument('input-path', default = 'assets/anecdotes.tsv')
@argument('output-path', default = 'assets/anecdotes')
def speak(input_path: str, output_path: str):
    makedirs(output_path, exist_ok = True)

    df = AnecdoteCollection.from_file(input_path).as_df

    client = CloudVoiceClient()

    df.dropna(inplace = True, subset = ('text', ))

    for i, row in df[~df['text'].str.contains('http')].iloc[::-1].reset_index().iterrows():
        print(i, text := row['text'])

        output_file_path = os_path.join(output_path, f'{i:06d}-{row["id"]}.mp3')

        segments = segment(add_sentence_terminators(text))

        # for segment_ in segments:
        #     print(segment_)
        #     print(len(segment_))

        speech = segments[0] | pipe | client.tts | pipe | BytesIO | pipe | AudioSegment.from_file

        for segment_ in segments[1:]:
            speech = speech.append(segment_ | pipe | client.tts | pipe | BytesIO | pipe | AudioSegment.from_file)

        speech.export(output_file_path, format = 'mp3')

        dd


if __name__ == '__main__':
    main()
