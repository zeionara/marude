import librosa
from .conversion import DEFAULT_SAMPLING_RATE


def get_duration(input_path: str, sampling_rate = DEFAULT_SAMPLING_RATE):  # wav file
    y, fs = librosa.load(input_path, sr = sampling_rate)
    n_frames = len(y)
    audio_length = n_frames * (1 / fs)

    return audio_length
