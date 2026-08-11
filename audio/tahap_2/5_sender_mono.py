import numpy as np
import alsaaudio

FREQ_0 = 1000
FREQ_1 = 2000
READY_FREQ = 3000

BIT_TIME = 0.01

RATE = 48000
CHANNELS = 1
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
PREAMBLE = "1010101010101010"
SAMPLES_PER_BIT = int(RATE * BIT_TIME)

DEIVCE_OUTPUT = "hw:0,7"

def tone(freq, duration):
    samples = int(RATE * duration)
    t = np.arange(samples) / RATE
    return np.sin(2 * np.pi * freq * t)

def encode(text):
    bits = ""
    for b in text.encode(): bits += format(b, "08b")
    return bits

def modulate(bits):
    output = []
    for bit in bits:
        if bit == "0": output.append(tone(FREQ_0, BIT_TIME))
        else: output.append(tone(FREQ_1, BIT_TIME))
    return np.concatenate(output)

def send_to_audio(pcm, buffer):
    for i in range(0, len(buffer), SAMPLES_PER_BIT):
        chunk = buffer[i:i + SAMPLES_PER_BIT]
        pcm_out.write(chunk.tobytes())

pcm_out = alsaaudio.PCM(
    type=alsaaudio.PCM_PLAYBACK,
    mode=alsaaudio.PCM_NORMAL,
    device=DEIVCE_OUTPUT,
    channels=CHANNELS,
    rate=RATE,
    format=FORMAT,
    periodsize=SAMPLES_PER_BIT
)

message = input("Masukkan pesan: ")

silence = np.zeros(int(RATE * 0.1))
ready = tone(READY_FREQ, 0.5)
audio = modulate(PREAMBLE + encode(message))
audio = np.concatenate([ready, audio, silence])
audio_int16 = (audio * 32767).astype(np.int16)

print("Mengirim READY frequency...")
send_to_audio(pcm_out, audio_int16)
print("Selesai dikirim.")

pcm_out.close()