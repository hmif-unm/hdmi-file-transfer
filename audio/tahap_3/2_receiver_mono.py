import alsaaudio
import numpy as np
import sys
import zlib

RATE = 48000
CHANNELS = 1
PERIODSIZE = 480

FREQ_0 = 1000
FREQ_1 = 2000
READY_FREQ = 3000

PREAMBLE = "1010101010101010"

DEVICE_INPUT = 'hw:2,0'

t = np.arange(PERIODSIZE) / RATE

sin_ready = np.sin(2 * np.pi * READY_FREQ * t)
cos_ready = np.cos(2 * np.pi * READY_FREQ * t)
sin_0 = np.sin(2 * np.pi * FREQ_0 * t)
cos_0 = np.cos(2 * np.pi * FREQ_0 * t)
sin_1 = np.sin(2 * np.pi * FREQ_1 * t)
cos_1 = np.cos(2 * np.pi * FREQ_1 * t)

def detect_ready(chunk):
    chunk = chunk.astype(np.float64)
    chunk -= np.mean(chunk)

    rms = np.sqrt(np.mean(chunk ** 2))

    if rms == 0: return False

    power_ready = correlation_power(chunk, sin_ready, cos_ready)
    power_0 = correlation_power(chunk, sin_0, cos_0)
    power_1 = correlation_power(chunk, sin_1, cos_1)

    return power_ready > power_0 and power_ready > power_1

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

    if power_0 > power_1: return "0"
    return "1"

def read_header(buffer):
    file_size = int.from_bytes(buffer[0:8], "big")
    crc32_hash = int.from_bytes(buffer[8:12], "big")

    return file_size, crc32_hash

if (len(sys.argv) < 3):
    print("Argument: " + sys.argv[0] + " <save name file> <input audio id>")
else:
    pcm = alsaaudio.PCM(
        type=alsaaudio.PCM_CAPTURE,
        mode=alsaaudio.PCM_NORMAL,
        device=sys.argv[2],
        channels=CHANNELS,
        rate=RATE,
        format=alsaaudio.PCM_FORMAT_S16_LE,
        periodsize=PERIODSIZE
    )

    buffer = np.array([], dtype=np.int16)
    received_bits = ""
    is_preamble_found = False

    print("[LOG] Menunggu sender...")

    try:
        while True:
            length, data = pcm.read()
            if length <= 0: continue
            samples = np.frombuffer(data, dtype=np.int16)

            buffer = np.concatenate([buffer, samples])

            while len(buffer) >= PERIODSIZE:
                chunk = buffer[:PERIODSIZE]
                buffer = buffer[PERIODSIZE:]

                if not is_preamble_found:
                    bit = detect_bit(chunk)
                    if bit is None: continue

                    received_bits += bit

                    if received_bits.find(PREAMBLE) != -1:
                        print("[LOG] Sender ditemukan! sedang diproses...")
                        is_preamble_found = True
                        received_bits = ""
                    continue
                else:
                    bit = detect_bit(chunk)
                    if bit is None:
                        print("[LOG] Berhasil menerima semua buffer file! mengecek file...")
                        saved_buffer = bytearray()

                        for i in range(0, len(received_bits) - 7, 8): saved_buffer.append(int(received_bits[i:i + 8], 2))

                        file_size, crc32_hash = read_header(saved_buffer)
                        saved_buffer = saved_buffer[12:]

                        if file_size != len(saved_buffer):
                            print(
                                f"[ERROR] Panjang file tidak sesuai! "
                                f"Mendapat {len(saved_buffer)} bytes, "
                                f"seharusnya {file_size} bytes"
                            )
                            exit(0)

                        print("[LOG] Panjang file sesuai: " + str(file_size) + " bytes")
                        
                        if zlib.crc32(saved_buffer) != crc32_hash:
                            print(
                                f"[ERROR] CRC32 tidak sesuai! "
                                f"Mendapat {hex(zlib.crc32(saved_buffer))}, "
                                f"seharusnya {hex(crc32_hash)}"
                            )
                            exit(0)

                        print("[LOG] CRC32 Sesuai: " + hex(crc32_hash))
                        
                        with open(sys.argv[1], "wb") as f:
                            f.write(saved_buffer)
                        print("[LOG] File berhasil di simpan!")

                        exit(0)
                        break

                    received_bits += bit

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        pcm.close()