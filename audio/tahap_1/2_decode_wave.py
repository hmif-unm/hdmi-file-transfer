import wave
import numpy as np

SAMPLE_RATE = 48000
BIT_DURATION = 0.1

FREQ_0 = 1000
FREQ_1 = 2000

SAMPLES_PER_BIT = int(SAMPLE_RATE * BIT_DURATION)

# buka file WAV
with wave.open("output.wav", "rb") as wav:
    sample_rate = wav.getframerate()
    channels = wav.getnchannels()
    sample_width = wav.getsampwidth()

    raw_data = wav.readframes(wav.getnframes())

audio = np.frombuffer(raw_data, dtype=np.int16) # ubah raw bytes menjadi sample int16
decoded_bits = "" # tempat nyimpen deocde bits nya

# proses audio setiap 0.1 detik
for start in range(0, len(audio), SAMPLES_PER_BIT):
    samples = audio[start:start + SAMPLES_PER_BIT] # dari sample awal sampe sample * 0.1 detik
    if len(samples) < SAMPLES_PER_BIT: break # jika sample nya nggak sample_per_bit, maka abaikan aja

    # waktu untuk setiap sample (0.1 detik)
    t = np.arange(len(samples)) / SAMPLE_RATE

    # buat referensi sine wave
    wave_0 = np.sin(2 * np.pi * FREQ_0 * t)
    wave_1 = np.sin(2 * np.pi * FREQ_1 * t)

    # hitung cocok nya
    score_0 = np.sum(samples * wave_0)
    score_1 = np.sum(samples * wave_1)

    # menentukan bit dengan frekuensi yang lebih kuat
    if score_0 > score_1: decoded_bits += "0"
    else: decoded_bits += "1"

print("Decoded:", decoded_bits)
