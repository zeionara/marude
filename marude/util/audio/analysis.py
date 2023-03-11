import taglib
from pydub.utils import mediainfo
import librosa

WEBRTC_VAD_SUPPORTED_SAMPLING_RATES = (8000, 16000, 32000, 48000)
N_WEBRTC_VAD_SUPPORTED_SAMPLING_RATES = len(WEBRTC_VAD_SUPPORTED_SAMPLING_RATES)


def get_sampling_rate(input_path: str) -> int:
    return int(mediainfo(input_path)["sample_rate"])


# def get_title(input_path: str) -> int:
#     # return mediainfo(input_path)
#     return taglib.File(input_path).tags


def refresh_tags(input_path: str) -> int:
    taglib.File(input_path).save()


def set_part(input_path: str, part_index: int, n_parts: int, width: int, default_title: str) -> int:
    # return mediainfo(input_path)
    part = eval(f'f"{{part_index:0{width}d}}/{{n_parts:0{width}d}}"')
    file = taglib.File(input_path)

    if 'TITLE' in (tags := file.tags):
        title = ' '.join(tags['TITLE'])
    else:
        title = default_title

    file.tags['TITLE'] = [f"{title} {part}"]
    file.tags['PART'] = [part]
    file.tags['PART_INDEX'] = [str(part_index)]
    file.tags['N_PARTS'] = [str(n_parts)]
    file.save()


def pick_webrtc_vad_supported_sampling_rate(rate: int) -> int:
    i = 0
    while True:
        if i >= N_WEBRTC_VAD_SUPPORTED_SAMPLING_RATES:
            return WEBRTC_VAD_SUPPORTED_SAMPLING_RATES[-1]

        if (current_rate := WEBRTC_VAD_SUPPORTED_SAMPLING_RATES[i]) >= rate:
            return current_rate

        i += 1


def get_duration(input_path: str):  # wav file
    y, fs = librosa.load(input_path, sr = get_sampling_rate(input_path))
    n_frames = len(y)
    audio_length = n_frames * (1 / fs)

    return audio_length
