from pydub.utils import mediainfo
import librosa

WEBRTC_VAD_SUPPORTED_SAMPLING_RATES = (8000, 16000, 32000, 48000)
N_WEBRTC_VAD_SUPPORTED_SAMPLING_RATES = len(WEBRTC_VAD_SUPPORTED_SAMPLING_RATES)


def get_sampling_rate(input_path: str) -> int:
    return int(mediainfo(input_path)["sample_rate"])


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
