from os import makedirs, path as os_path, remove, walk
from multiprocessing import Queue, Process

from click import group, argument, option, Choice
from tasty import pipe
from tqdm import tqdm
import taglib
# from pydub.utils import mediainfo
import ffmpeg

from ..util.path import drop_extension, add_extension, Extension, has_extension
from ..util.audio import split as split_

from ..CloudVoiceClient import CloudVoiceClient, Voice


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
@option('--chapters', '-c', is_flag = True)
def split(input_path: str, output_path: str, shortest_silence: float, shortest_part: float, longest_part: float, chapters: bool):
    if output_path is None:
        makedirs(output_path := input_path | pipe | drop_extension, exist_ok = True)

    if chapters:
        assert has_extension(input_path, Extension.M4B), 'Input file has an incorrect extension, expected: m4b'
        meta = ffmpeg.probe(input_path, show_chapters = None)
        input_stream = ffmpeg.input(input_path)

        for chapter in tqdm(meta['chapters'], desc = 'Converting chapters'):
            chapter_title = chapter['tags']['title']
            # chapTitle = re.sub("['-]", "", chapTitle)
            start_time = chapter['start_time']
            end_time = chapter['end_time']
            # chap_number = chapter['id'] + 1

            track_name = f'{chapter_title}.{Extension.MP3.value}'

            outbound = ffmpeg.output(input_stream, os_path.join(output_path, track_name), ss = start_time, to = end_time, map_chapters = '-1')
            ffmpeg.run(outbound)

            # outbound = ffmpeg.output(bookFile,trackName,ss=startTime,to=endTime,map_chapters="-1")
            # ffmpeg.run(outbound)
        # file = taglib.File(input_path)
        # print(file.tags)
        # meta = mediainfo(input_path)
        # print(meta)
        return

    split_(input_path, output_path, shortest_silence, longest_part, shortest_part)


@main.command()
@argument('input-path', type = str)
def rename(input_path: str):
    for root, _, files in walk(input_path):
        for file in files:
            tags = (file_ := taglib.File(os_path.join(root, file))).tags

            tags['TITLE'] = [f"{file | pipe | drop_extension} {tags['ALBUM'][0]}"]
            file_.save()
