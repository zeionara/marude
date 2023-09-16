from os import makedirs, path
from io import BytesIO
from datetime import datetime
from pathlib import Path

from click import argument, option
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pandas import read_csv, concat
from tasty import pipe

from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

from ..Anecdote import AnecdoteCollection
from ..util.string import segment, add_sentence_terminators
from ..CloudVoiceClient import CloudVoiceClient

from .main import main


@main.group()
def anecdote():
    pass


@anecdote.command()
@argument('output-path', type = str)
@option('--batch-size', '-b', type = int, default = 100)
@option('--after', '-a', type = str, default = None)
@option('--community', '-c', type = str, default = 'anekdotikategoriib')
@option('--max-n-batches', '-n', type = int, default = None)
@option('--verbose', '-v', is_flag = True)
def fetch(output_path: str, batch_size: int, after: str, community: str, max_n_batches: int, verbose: bool):
    if after is None:
        AnecdoteCollection.from_vk(
            community, datetime.now(), batch_size = batch_size, max_n_batches = max_n_batches, verbose = verbose
        ).as_df.to_csv(output_path, sep = '\t', index = False)
    else:
        anecdotes = AnecdoteCollection.from_file(after)
        AnecdoteCollection.from_vk(
            community, datetime.now(), batch_size = batch_size, after = anecdotes, max_n_batches = max_n_batches, verbose = verbose
        ).as_df.to_csv(output_path, sep = '\t', index = False)


@anecdote.command()
@argument('text', type = str)
def bark(text: str):
    preload_models()

    audio = generate_audio(text)

    write_wav('assets/audio.wav', SAMPLE_RATE, audio)


@anecdote.command()
@argument('path', type = str)
def stats(path: str):
    df = read_csv(path, sep = '\t')

    texts = df['text'].astype(str).tolist()

    print(f'{len(texts)} anecdotes')

    n_characters = 0

    for text in texts:
        n_characters += len(text)

    print(f'{n_characters} characters')


@anecdote.command()
@argument('input-path', type = str, default = 'assets/anecdotes.tsv')
def explore(input_path: str):
    for date in read_csv(input_path, sep = '\t').published:
        print(date)


@anecdote.command(name = 'tts')
@argument('input-path', default = 'assets/anecdotes.tsv')
@argument('output-path', default = 'assets/anecdotes')
def anecdote_tts(input_path: str, output_path: str):
    makedirs(output_path, exist_ok = True)

    df = AnecdoteCollection.from_file(input_path).as_df

    client = CloudVoiceClient()

    df.dropna(inplace = True, subset = ('text', ))

    for i, row in df[~df['text'].str.contains('http')].iloc[::-1].reset_index().iterrows():
        output_file_path = path.join(output_path, f'{i:06d}-{row["id"]}.mp3')

        if path.isfile(output_file_path):
            continue

        print(i, text := row['text'])

        segments = segment(add_sentence_terminators(text))

        # for segment_ in segments:
        #     print(segment_)
        #     print(len(segment_))

        try:
            speech = segments[0] | pipe | client.tts | pipe | BytesIO | pipe | AudioSegment.from_file

            for segment_ in segments[1:]:
                speech = speech.append(segment_ | pipe | client.tts | pipe | BytesIO | pipe | AudioSegment.from_file)
        except CouldntDecodeError:
            print(f'Cannot handle text "{text}" and save result as {output_file_path}. Skipping.')
            continue

        speech.export(output_file_path, format = 'mp3')


@anecdote.command()
@argument('input-paths', nargs = -1, type = str)
@argument('output-path', nargs = 1, type = str)
def merge(input_paths: tuple[str], output_path: str):
    dfs = []

    for input_path in input_paths:
        local_df = read_csv(input_path, sep = '\t')
        local_df['source'] = Path(input_path).stem

        dfs.append(local_df)

    # print(concat(dfs).reset_index())
    concat(dfs).to_csv(output_path, sep = '\t', index = False)
