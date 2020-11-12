import base64
import json
import logging
import subprocess

from boto3 import client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def synthesize(text: str = "", translate: bool = False, fmt='mp3') -> str:
    """ Synthesize the provided text to base64 encoded mp3
    :param text: text to be synthesized
    :param translate: bool needs to be translated into German
    :param fmt: 'wav' or 'mp3'
    :return: string, the base64 encoded bytes or a wav or mp3 file
    """
    response = client("polly").synthesize_speech(Engine="standard" if translate else "neural",
                                                 VoiceId="Marlene" if translate else "Joanna",
                                                 Text=to_german(text) if translate else text,
                                                 OutputFormat="mp3")
    binary_data = response["AudioStream"].read()
    return base64.b64encode(mpeg2wav(binary_data) if fmt == 'wav' else binary_data).decode("utf-8")


def to_german(english: str) -> str:
    """
    Calling our translate lambda function
    doc: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
    """
    response = client('lambda').invoke(
        FunctionName='EN2DE',
        InvocationType='RequestResponse',
        Payload=bytes(json.dumps({'text': english}), encoding='utf8')
    )
    logger.info(str(response))
    response = json.load(response['Payload'])
    return response.get('TranslatedText')


def mpeg2wav(mp3_bytes: bytes) -> bytes:
    """
    :param mp3_bytes: raw mp3 data
    :return: wav bytes prefixed with the proper header
    """
    wav_bytes = subprocess.Popen(["/tmp/ffmpeg", "-i", "pipe:0", "-f", "wav", "pipe:1"],
                                 shell=False,
                                 stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE).communicate(mp3_bytes)[0]
    return create_header(22000, 16, 1, len(str(wav_bytes))) + wav_bytes


def create_header(sample_rate: int, bit_size: int, channels: int, len_samples: int) -> bytes:
    """
    :param sample_rate: e.g 22000
    :param bit_size: e.g. 16
    :param channels: e.g. 1 for mono, 2 for stereo
    :param len_samples: length of the raw wav bytes
    :return: header info starting with RIFF
    """
    data_size = len_samples * channels * bit_size // 8
    header = bytes("RIFF", 'ascii')  # (4byte) Marks file as RIFF
    header += (data_size + 36).to_bytes(4, 'little')  # (4byte) File size in bytes excluding this and RIFF marker
    header += bytes("WAVE", 'ascii')  # (4byte) File type
    header += bytes("fmt ", 'ascii')  # (4byte) Format Chunk Marker
    header += (16).to_bytes(4, 'little')  # (4byte) Length of above format data
    header += (1).to_bytes(2, 'little')  # (2byte) Format type (1 - PCM)
    header += channels.to_bytes(2, 'little')  # (2byte)
    header += sample_rate.to_bytes(4, 'little')  # (4byte)
    header += (sample_rate * channels * bit_size // 8).to_bytes(4, 'little')  # (4byte)
    header += (channels * bit_size // 8).to_bytes(2, 'little')  # (2byte)
    header += bit_size.to_bytes(2, 'little')  # (2byte)
    header += bytes("data", 'ascii')  # (4byte) Data Chunk Marker
    header += data_size.to_bytes(4, 'little')  # (4byte) Data size in bytes
    return header
