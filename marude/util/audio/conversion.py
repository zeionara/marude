from os import system as run, path

FFMPEG_BIN = 'ffmpeg'
DEFAULT_SAMPLING_RATE = 16000
N_CHANNELS = 1
DEFAULT_N_THREADS = 4  # number of threads does not seem to have an effect (ffmpeg in any case uses just one thread)


def to_wav(input_path: str, output_path: str, sampling_rate: int = DEFAULT_SAMPLING_RATE):
    run(f'{FFMPEG_BIN} -i {input_path} -acodec pcm_s16le -ar {sampling_rate} -ac {N_CHANNELS} {output_path} -y -loglevel panic -threads {DEFAULT_N_THREADS}')

    # try:
    #     cmd = f'{FFMPEG_BIN} -i {input_path} -acodec pcm_s16le -ar 16000 -ac 1 {output_path} -y -loglevel panic'
    #     run(cmd)
    #     return True
    # except Exception as error:
    #     print(f'Error: {repr(error)}')
    #     return False


def trim_audio_ffmpeg(input_path: str, segment_path: str, begin_timestamp: float, end_timestamp: float, sampling_rate: int = DEFAULT_SAMPLING_RATE):
    if not path.exists(input_path):
        return False

    command = (
        f'{FFMPEG_BIN} -i {input_path} -ar {sampling_rate} -ac {N_CHANNELS} ' +
        # f'-filter "aresample=isr={sampling_rate}:osr={sampling_rate}:dither_method=triangular_hp:resampler=swr:filter_type=cubic" ' +
        f'-ss {begin_timestamp:.2f} -to {end_timestamp:.2f} {segment_path} -y -loglevel panic -threads {DEFAULT_N_THREADS}'
    )

    # print(command)

    run(command)

    return True

    # try:
    #     run(
    #         '{FFMPEG_BIN} -i {input_path} -ar {sampling_rate} -ac 1 -filter '+
    #         '"aresample=isr=44100:osr={sampling_rate}:dither_method=triangular_hp:resampler=swr:filter_type=cubic"'+
    #         '-ss {begin_timestamp:.2f} -to {end_timestamp:.2f} {segment_path} -y -loglevel panic'
    #     )
    #     return True
    # except Exception as error:
    #     print('Error: {}'.format(repr(error)))
    #     return False
