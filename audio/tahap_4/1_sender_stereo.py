import numpy as np
import alsaaudio
import sys
import zlib

FREQ_0 = 1000
FREQ_1 = 2000
READY_FREQ = 3000

BIT_TIME = 0.01

RATE = 48000
CHANNELS = 2
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
PREAMBLE = "1010101010101010"
SAMPLES_PER_BIT = int(RATE * BIT_TIME)
FILE_BUFFER = ""

def tone(freq, duration):
    samples = int(RATE * duration)
    t = np.arange(samples) / RATE
    return np.sin(2 * np.pi * freq * t)

def encode_buffer(buffer):
    bits = ""
    for b in buffer: bits += format(b, "08b")
    return bits

def modulate(bits):
    output = []
    for i in range(0, len(bits), 2):
        left_bit = bits[i]
        right_bit = bits[i + 1]

        left = tone(FREQ_0 if left_bit == "0" else FREQ_1, BIT_TIME)
        right = tone(FREQ_0 if right_bit == "0" else FREQ_1, BIT_TIME)

        # sekarang kita gabungin jadi stereo
        stereo = np.column_stack((left, right))
        output.append(stereo)

    return np.concatenate(output)

def send_to_audio(pcm, buffer):
    for i in range(0, len(buffer), SAMPLES_PER_BIT):
        chunk = buffer[i:i + SAMPLES_PER_BIT]
        pcm_out.write(chunk.tobytes())

def make_header(file_data):
    file_size = len(file_data)
    crc32_hash = zlib.crc32(file_data)

    header = (
        b"HDMItA" +
        file_size.to_bytes(8, "big") +
        crc32_hash.to_bytes(4, "big")
    )

    return header

if (len(sys.argv) < 3):
    print("Argument: " + sys.argv[0] + " <name file> <output audio id>")
else:
    pcm_out = alsaaudio.PCM(
        type=alsaaudio.PCM_PLAYBACK,
        mode=alsaaudio.PCM_NORMAL,
        device=sys.argv[2],
        channels=CHANNELS,
        rate=RATE,
        format=FORMAT,
        periodsize=SAMPLES_PER_BIT
    )

    with open(sys.argv[1], "rb") as f:
        FILE_BUFFER = f.read()

    silence = np.zeros(int(RATE * 1.0))
    ready = tone(READY_FREQ, 0.5)

    silence = np.column_stack((silence, silence))
    ready = np.column_stack((ready, ready))
    audio = modulate(PREAMBLE + encode_buffer(make_header(FILE_BUFFER)) + encode_buffer(FILE_BUFFER))
    audio = np.concatenate([ready, audio, silence])
    audio_int16 = (audio * 32767).astype(np.int16)

    print("[LOG] Mengirim READY frekuensi agar tersinkron...")
    send_to_audio(pcm_out, audio_int16)
    print("[LOG] Selesai dikirim.")

    pcm_out.close()