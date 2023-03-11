# parts of code are borrowed from https://github.com/gkrsv/split_audio.git

from multiprocessing import Queue
from os import remove, path
import contextlib

from dataclasses import dataclass

import wave

from webrtcvad import Vad
from tasty import pipe

from ..path import drop_extension, add_extension, Extension
from ..number import get_width
from .conversion import to_wav, trim_audio_ffmpeg, N_CHANNELS, DEFAULT_SAMPLING_RATE
from .analysis import get_duration, set_part, refresh_tags, WEBRTC_VAD_SUPPORTED_SAMPLING_RATES  # , get_sampling_rate, pick_webrtc_vad_supported_sampling_rate
from .Frame import Frame


VAD_AGGRESSIVENESS_CODE = 3  # 0, 1, 2, or 3 (3 is the highest)


@dataclass
class Segment:
    begin_timestamp: float
    end_timestamp: float

    @property
    def duration(self):
        return self.end_timestamp - self.begin_timestamp


@dataclass
class SegmentIsReadyMessage:
    path: str
    last: bool = False


def read_wave(input_path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(input_path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == N_CHANNELS  # configured in to_wav
        # sample_width = wf.getsampwidth()
        # assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in WEBRTC_VAD_SUPPORTED_SAMPLING_RATES  # configured in to_wav
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def vad_audio_segment(input_path, gap_size=0.5, frame_duration=10):
    """
    :param audio_file:
    :param gap_size: gap between neighbour segments (seconds)
    :param frame_duration: frame step (mili seconds)
    :return:
    """
    vad = Vad(VAD_AGGRESSIVENESS_CODE)

    audio, sample_rate = read_wave(input_path)

    vad_segment = []
    for frame in Frame.from_pcm(frame_duration, audio, sample_rate):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            vad_segment.append(Segment(frame.timestamp, frame.timestamp + frame.duration))

    if len(vad_segment) == 0:
        return tuple()

    audio_segment = [vad_segment[0]]
    for x in vad_segment[1:]:
        if x.begin_timestamp <= audio_segment[-1].end_timestamp + gap_size:
            audio_segment[-1].end_timestamp = x.end_timestamp
        else:
            audio_segment.append(x)

    return audio_segment


def split(input_path: str, output_path: str, min_silence: float, max_duration: float, min_duration: float, queue: Queue = None, sampling_rate: int = None):

    if sampling_rate is None:
        # sampling_rate = input_path | pipe | get_sampling_rate | pipe | pick_webrtc_vad_supported_sampling_rate
        sampling_rate = DEFAULT_SAMPLING_RATE

    converted_path = add_extension(f'{drop_extension(input_path)}-converted', Extension.WAV)

    print(f"Started converting {input_path} to .wav which is saved as {converted_path}")
    to_wav(input_path, output_path = converted_path, sampling_rate = sampling_rate)
    refresh_tags(converted_path)

    duration = get_duration(converted_path)
    print(f"Finished converting {input_path} to .wav which is saved as {converted_path}. Audio duration is {duration} seconds")

    print(f"Started segmenting {converted_path}")
    segments = vad_audio_segment(converted_path)
    print(f"Finished segmenting {converted_path}. There are {len(segments)} segments")

    if len(segments) == 0:
        print("No segments to split")
        return

    try:
        remove(converted_path)
    except:
        pass

    # make a segment using min/max length
    final_list = []
    temp_segment = segments[0]

    for x in segments[1:]:
        # cur_duration = x[1] - x[0]
        # temp_duration = temp_segment[1] - temp_segment[0]

        # try to split on silences no shorter than min duration
        if x.begin_timestamp - temp_segment.end_timestamp <= min_silence:
            temp_segment.end_timestamp = x.end_timestamp
            continue  # TODO: Add a stricter rule

        if x.duration + temp_segment.duration > max_duration:
            final_list.append(temp_segment)
            temp_segment = x
        else:
            temp_segment.end_timestamp = x.end_timestamp

    final_list.append(temp_segment)
    n_segments = len(final_list)
    print(f"Final number of segments is {n_segments}")

    if final_list[-1].duration <= min_duration:
        mean_time = (final_list[-2].begin_timestamp + final_list[-1].end_timestamp) / 2
        final_list[-2].end_timestamp = mean_time
        final_list[-1].begin_timestamp = mean_time

    final_list[0].begin_timestamp = 0
    final_list[-1].end_timestamp = duration

    path_index_width = get_width(len(final_list) - 1)
    log_index_width = get_width(len(final_list))

    path_formatter = f'f"{{i:0{path_index_width}d}}"'
    progress_log_formatter = f'f"Finished saving {{i + 1:0{log_index_width}d}}/{{n_segments:0{log_index_width}d}} segments. The latest segment was saved as {{segment_path}}"'

    default_title = input_path | pipe | drop_extension | pipe | path.basename

    print("Started saving segments on disk")
    for i, seg in enumerate(final_list):
        stime = seg.begin_timestamp
        etime = seg.end_timestamp

        if i == 0:
            etime = (etime + final_list[i + 1].begin_timestamp) / 2
        elif i == len(final_list) - 1:
            stime = (stime + final_list[i - 1].end_timestamp) / 2
        else:
            stime = (stime + final_list[i - 1].end_timestamp) / 2
            etime = (etime + final_list[i + 1].begin_timestamp) / 2

        segment_path = add_extension(path.join(output_path, eval(path_formatter)), Extension.WAV)
        trim_audio_ffmpeg(input_path, segment_path, stime, etime, sampling_rate = sampling_rate)
        print(eval(progress_log_formatter))

        set_part(segment_path, part_index = i + 1, n_parts = n_segments, width = log_index_width, default_title = default_title)
        # print(get_title(segment_path))

        if queue is not None:
            queue.put(SegmentIsReadyMessage(path = segment_path, last = i == n_segments - 1), block = False)
