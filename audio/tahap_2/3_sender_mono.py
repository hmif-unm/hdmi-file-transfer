import numpy as np
import alsaaudio

FREQ_0 = 1000
FREQ_1 = 2000
BIT_TIME = 0.01 # berarti 1 bit = 10ms

RATE = 48000
CHANNELS = 1
FORMAT = alsaaudio.PCM_FORMAT_S16_LE

PREAMBLE = "1010101010101010"

SAMPLES_PER_BIT = int(RATE * BIT_TIME) # perhitungan sample per bit

def tone(freq):
    t = np.arange(SAMPLES_PER_BIT) / RATE
    return np.sin(2 * np.pi * freq * t)

def encode(text):
    bits = ""
    for b in text.encode(): bits += format(b, "08b")
    return bits

def modulate(bits):
    output = []
    for bit in bits:
        if bit == "0": output.append(tone(FREQ_0))
        else: output.append(tone(FREQ_1))
    return np.concatenate(output)

pcm_out = alsaaudio.PCM(
    type=alsaaudio.PCM_PLAYBACK,
    mode=alsaaudio.PCM_NORMAL,
    device='hw:0,7',
    channels=CHANNELS,
    rate=RATE,
    format=FORMAT,
    periodsize=SAMPLES_PER_BIT
)

message = input("Masukkan pesan: ")
audio = modulate(PREAMBLE + encode(message))

silence = np.zeros(int(RATE * 0.5))
audio = np.concatenate([silence, audio, silence])

audio_int16 = (audio * 32767).astype(np.int16)

print("Mengirim...")

for i in range(0, len(audio_int16), SAMPLES_PER_BIT):
    chunk = audio_int16[i:i + SAMPLES_PER_BIT]
    pcm_out.write(chunk.tobytes())

print("Selesai dikirim.")
pcm_out.close()