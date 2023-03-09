from tasty import pipe
from marude import CloudVoiceClient, Voice


if __name__ == '__main__':

    client = CloudVoiceClient(Voice.MARIA)

    with open('message-1.mp3', 'wb') as file:
        _ = 'Съешь еще этих мягких французских булок' | pipe | client.tts | pipe | file.write

    with open('message-2.mp3', 'wb') as file:
        _ = 'да выпей чаю' | pipe | client.tts | pipe | file.write
