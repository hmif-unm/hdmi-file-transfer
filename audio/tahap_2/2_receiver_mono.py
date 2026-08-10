import alsaaudio
import numpy as np

DEVICE = "hw:1,0"

RATE = 48000
CHANNELS = 1
PERIODSIZE = 480

FREQ_0 = 1000
FREQ_1 = 2000

t = np.arange(PERIODSIZE) / RATE

sin_0 = np.sin(2 * np.pi * FREQ_0 * t)
cos_0 = np.cos(2 * np.pi * FREQ_0 * t)

sin_1 = np.sin(2 * np.pi * FREQ_1 * t)
cos_1 = np.cos(2 * np.pi * FREQ_1 * t)

def correlation_power(chunk, sin_wave, cos_wave):
    I = np.sum(chunk * cos_wave)
    Q = np.sum(chunk * sin_wave)

    return I * I + Q * Q

def detect_bit(chunk):
    chunk = chunk.astype(np.float64)

    chunk -= np.mean(chunk)

    rms = np.sqrt(np.mean(chunk ** 2))

    if rms == 0: return None

    power_0 = correlation_power(chunk, sin_0, cos_0)
    power_1 = correlation_power(chunk, sin_1, cos_1)

    total = power_0 + power_1

    if total == 0: return None

    confidence = abs(power_0 - power_1) / total

    if confidence < 0.2: return None
    if power_0 > power_1: return "0"
    return "1"

pcm = alsaaudio.PCM(
    type=alsaaudio.PCM_CAPTURE,
    mode=alsaaudio.PCM_NORMAL,
    device=DEVICE,
    channels=CHANNELS,
    rate=RATE,
    format=alsaaudio.PCM_FORMAT_S16_LE,
    periodsize=PERIODSIZE
)

print("menunggu data...")

buffer = np.array([], dtype=np.int16)
received_bits = ""
is_process_audio = False

try:
    while True:
        length, data = pcm.read()
        if length <= 0: continue

        samples = np.frombuffer(data, dtype=np.int16)
        buffer = np.concatenate([buffer, samples])

        while len(buffer) >= PERIODSIZE:
            chunk = buffer[:PERIODSIZE]
            buffer = buffer[PERIODSIZE:]

            bit = detect_bit(chunk)

            if bit is None:
                if not is_process_audio: continue

                print("mendapatkan bits:", received_bits)
                message = ""

                for i in range(0, len(received_bits) - 7, 8):
                    byte_bits = received_bits[i:i + 8]
                    value = int(byte_bits, 2)
                    message += chr(value)

                print("isi message:", repr(message))
                received_bits = ""
                exit(0)
            else: is_process_audio = True

            received_bits += bit

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    pcm.close()