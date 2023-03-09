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

The module can be used programmatically as well. First, install the module through [pip](https://pypi.org/project/marude/):

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
