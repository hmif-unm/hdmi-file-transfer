import alsaaudio
import numpy as np
import sys
import zlib

RATE = 48000
CHANNELS = 2                     # stereo
PERIODSIZE = 480                 # jumlah sampel per bit (0.01 detik)

FREQ_0 = 1000
FREQ_1 = 2000
READY_FREQ = 3000

PREAMBLE = "1010101010101010"

# vektor waktu untuk satu periode
t = np.arange(PERIODSIZE) / RATE

# gelombang referensi untuk korelasi (mono, akan diaplikasikan per kanal)
sin_0 = np.sin(2 * np.pi * FREQ_0 * t)
cos_0 = np.cos(2 * np.pi * FREQ_0 * t)
sin_1 = np.sin(2 * np.pi * FREQ_1 * t)
cos_1 = np.cos(2 * np.pi * FREQ_1 * t)

def correlation_power(chunk, sin_wave, cos_wave):
    I = np.sum(chunk * cos_wave)
    Q = np.sum(chunk * sin_wave)
    return I * I + Q * Q

def detect_bit(channel_data):
    channel_data = channel_data.astype(np.float64)
    channel_data -= np.mean(channel_data)

    rms = np.sqrt(np.mean(channel_data ** 2))
    if rms == 0: return None

    power_0 = correlation_power(channel_data, sin_0, cos_0)
    power_1 = correlation_power(channel_data, sin_1, cos_1)

    total = power_0 + power_1
    if total == 0: return None

    return "0" if power_0 > power_1 else "1"

def detect_bits_stereo(stereo_chunk):
    left_ch = stereo_chunk[:, 0]
    right_ch = stereo_chunk[:, 1]

    left_bit = detect_bit(left_ch)
    right_bit = detect_bit(right_ch)

    return left_bit, right_bit

def read_header(buffer):
    magic_header = buffer[0:6]
    file_size = int.from_bytes(buffer[6:14], "big")
    crc32_hash = int.from_bytes(buffer[14:18], "big")
    return magic_header, file_size, crc32_hash

if len(sys.argv) < 3:
    print("Argument: " + sys.argv[0] + " <save name file> <input audio id>")
    sys.exit(1)

pcm = alsaaudio.PCM(
    type=alsaaudio.PCM_CAPTURE,
    mode=alsaaudio.PCM_NORMAL,
    device=sys.argv[2],
    channels=CHANNELS,
    rate=RATE,
    format=alsaaudio.PCM_FORMAT_S16_LE,
    periodsize=PERIODSIZE
)

buffer = np.empty((0, 2), dtype=np.int16)   # menampung sampel stereo
received_bits = ""
is_preamble_found = False

print("[LOG] Menunggu sender...")

try:
    while True:
        length, data = pcm.read()
        if length <= 0: continue

        samples = np.frombuffer(data, dtype=np.int16)
        samples = samples.reshape(-1, 2)
        buffer = np.concatenate([buffer, samples])

        while len(buffer) >= PERIODSIZE:
            chunk = buffer[:PERIODSIZE]
            buffer = buffer[PERIODSIZE:]

            left_bit, right_bit = detect_bits_stereo(chunk)

            if not is_preamble_found:
                if left_bit is None or right_bit is None: continue
                received_bits += left_bit + right_bit

                if PREAMBLE in received_bits:
                    print("[LOG] Sender ditemukan! sedang diproses...")
                    is_preamble_found = True
                    received_bits = ""
                continue
            else:
                if left_bit is None and right_bit is None:
                    print("[LOG] Berhasil menerima semua buffer file! mengecek file...")
                    saved_buffer = bytearray()
                    for i in range(0, len(received_bits) - 7, 8):
                        saved_buffer.append(int(received_bits[i:i+8], 2))

                    magic_header, file_size, crc32_hash = read_header(saved_buffer)
                    saved_buffer = saved_buffer[18:]  # potong header

                    if magic_header != b"HDMItA":
                        print("[ERROR] Magic Header tidak sesuai!")
                        exit(0)

                    print("[LOG] Magic header sesuai!")

                    if file_size != len(saved_buffer):
                        print(
                            f"[ERROR] Panjang file tidak sesuai! "
                            f"Mendapat {len(saved_buffer)} bytes, "
                            f"seharusnya {file_size} bytes"
                        )
                        sys.exit(1)

                    print("[LOG] Panjang file sesuai: " + str(file_size) + " bytes")

                    if zlib.crc32(saved_buffer) != crc32_hash:
                        print(
                            f"[ERROR] CRC32 tidak sesuai! "
                            f"Mendapat {hex(zlib.crc32(saved_buffer))}, "
                            f"seharusnya {hex(crc32_hash)}"
                        )
                        sys.exit(1)

                    print("[LOG] CRC32 Sesuai: " + hex(crc32_hash))

                    with open(sys.argv[1], "wb") as f:
                        f.write(saved_buffer)
                    print("[LOG] File berhasil disimpan!")
                    sys.exit(0)

                if left_bit is None: left_bit = "0"
                if right_bit is None: right_bit = "0"

                received_bits += left_bit + right_bit

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    pcm.close()