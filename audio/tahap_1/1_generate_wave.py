import wave
import numpy as np

SAMPLE_RATE = 48000
BIT_DURATION = 0.1

FREQ_0 = 1000
FREQ_1 = 2000

bit = "01"

audio = [] # disini tempat array data audio

for b in bit:
    if b == "0": freq = FREQ_0
    elif b == "1": freq = FREQ_1
    else: raise ValueError("Bit harus 0 atau 1")

    samples = int(SAMPLE_RATE * BIT_DURATION) # 4800 samples setiap 0.1
    for i in range(samples): # nah, ini untuk buat sample nya. dan dibawah itu untuk membuat sine wave nya
        t = i / SAMPLE_RATE # mempresentasikan posisi sample i sebagai waktu
        sample = np.sin(2 * np.pi * freq * t) # perhitungan ini buat generate wave, dan sesuai dengan bit freq nya
        audio.append(int(sample * 32767)) # buffer sample nya append ke audio.

with wave.open("output.wav", "wb") as wav:
    wav.setnchannels(1)      # mono
    wav.setsampwidth(2)      # 16 bit per sample
    wav.setframerate(48000)  # framerate
    
    data = np.array(audio, dtype=np.int16) # convert setiap sample menjadi signed 16-bit integer
    wav.writeframes(data.tobytes()) # ini buat write frame nya