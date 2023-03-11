# Marude

**Maru**sia **de**mo interface - an http api client which allows to automatically convert russian short texts into speech using [vk cloud](https://mcs.mail.ru/).

## Installation

To create a conda environment and install dependencies use the following command:

```sh
conda create -f environment.yml
```

Then activate created environment:

```sh
conda activate marude
```

## Usage

After the environment is set up, the app can be used from the command line: 

```sh
python -m marude tts 'Привет, мир' -m pavel -p message.mp3
```

The provided text (which must be 1024 characters long or shorter) will be converted into speech and saved as an audiofile `message.mp3`. By default the file is saved at `assets/message.mp3`.

The module can be used programmatically as well. First, install the system-wise dependencies:

```sh
sudo apt-get update && sudo apt-get install ffmpeg libtag1-dev
```

Then, install the module through [pip](https://pypi.org/project/marude/):

```sh
pip install marude
```

Then run your script, which may look like this (see [example](examples/dummy.py)):

```py
from tasty import pipe
from marude import CloudVoiceClient, Voice


if __name__ == '__main__':

    client = CloudVoiceClient(Voice.MARIA)

    with open('message-1.mp3', 'wb') as file:
        _ = 'Съешь еще этих мягких французских булок' | pipe | client.tts | pipe | file.write

    with open('message-2.mp3', 'wb') as file:
        _ = 'да выпей чаю' | pipe | client.tts | pipe | file.write
```

### Automatic speech recognition

Automatic speech recognition (ASR) pipeline is implemented as a pair of services:

1. **producer** - splits input `mp3` file into chunks with given max-length on silence and converts audio to `wav` format;
2. **consumer** - as soon as producer completes converting the next chunk it loads the file and sends it to a remote service for recognition. Then it appends the recognized text to the output file.

Example of command for running the pipeline:

```sh
python -m marude asr assets/real-colonel.mp3
```

Example of log looks like this (the whole pipeline was completed in 28 seconds):

```sh
Finished converting assets/real-colonel.mp3 to .wav which is saved as assets/real-colonel-converted.wav. Audio duration is 1502.856 seconds
Started segmenting assets/real-colonel-converted.wav
Finished segmenting assets/real-colonel-converted.wav. There are 413 segments
Final number of segments is 15
Started saving segments on disk
Finished saving 01/15 segments. The latest segment was saved as assets/real-colonel/00.wav
Finished saving 02/15 segments. The latest segment was saved as assets/real-colonel/01.wav
Finished saving 03/15 segments. The latest segment was saved as assets/real-colonel/02.wav
Finished saving 04/15 segments. The latest segment was saved as assets/real-colonel/03.wav
Finished saving 05/15 segments. The latest segment was saved as assets/real-colonel/04.wav
Finished saving 06/15 segments. The latest segment was saved as assets/real-colonel/05.wav
Finished saving 07/15 segments. The latest segment was saved as assets/real-colonel/06.wav
Finished saving 08/15 segments. The latest segment was saved as assets/real-colonel/07.wav
Finished saving 09/15 segments. The latest segment was saved as assets/real-colonel/08.wav
Finished saving 10/15 segments. The latest segment was saved as assets/real-colonel/09.wav
Finished saving 11/15 segments. The latest segment was saved as assets/real-colonel/10.wav
Finished saving 12/15 segments. The latest segment was saved as assets/real-colonel/11.wav
Recognized text from file assets/real-colonel/00.wav
Finished saving 13/15 segments. The latest segment was saved as assets/real-colonel/12.wav
Finished saving 14/15 segments. The latest segment was saved as assets/real-colonel/13.wav
Finished saving 15/15 segments. The latest segment was saved as assets/real-colonel/14.wav
Recognized text from file assets/real-colonel/01.wav
Recognized text from file assets/real-colonel/02.wav
Recognized text from file assets/real-colonel/03.wav
Recognized text from file assets/real-colonel/04.wav
Recognized text from file assets/real-colonel/05.wav
Recognized text from file assets/real-colonel/06.wav
Recognized text from file assets/real-colonel/07.wav
Recognized text from file assets/real-colonel/08.wav
Recognized text from file assets/real-colonel/09.wav
Recognized text from file assets/real-colonel/10.wav
Recognized text from file assets/real-colonel/11.wav
Recognized text from file assets/real-colonel/12.wav
Recognized text from file assets/real-colonel/13.wav
Recognized text from file assets/real-colonel/14.wav
```

See details of this example [here](https://cutt.ly/marude-examples). There is also another example with 3-hour recording, which was handled in ~ 12 minutes.
