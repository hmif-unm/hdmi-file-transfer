# Tahap Pertama | Mengirim Pesan lewat HDMI

Di tahap pertama ini, kita mulai dari hal yang paling sederhana: **mencoba mengirim pesan melalui HDMI**.

Awalnya gw kepikiran satu pertanyaan:

> **"Kalau HDMI bisa mengirim gambar dan suara, apakah kita bisa memanfaatkannya untuk mengirim data lain?"**

Dari situ, gw coba mulai dari jalur audio HDMI.

## Ide Dasar

Karena HDMI bisa membawa sinyal audio, kita bisa memanfaatkan audio tersebut sebagai media untuk mengirim data.

Untuk percobaan pertama, gw menggunakan teknik yang sangat sederhana: **Frequency Shift Keying (FSK)**.

Konsepnya cukup gampang. Setiap bit direpresentasikan menggunakan frekuensi tertentu:

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

Jadi, misalnya data yang ingin dikirim adalah:

```text
01101000
```

Maka setiap bit akan diubah menjadi frekuensi:

```text
1000 Hz -> 2000 Hz -> 2000 Hz -> 1000 Hz
2000 Hz -> 1000 Hz -> 1000 Hz -> 1000 Hz
```

Di sisi pengirim, program akan membuat sinyal audio berdasarkan urutan frekuensi tersebut dan mengirimkannya melalui output audio HDMI.

Kemudian di sisi penerima, audio HDMI akan direkam dan dianalisis. Program akan mencari frekuensi yang sedang diterima, lalu menentukan apakah frekuensi tersebut mewakili `0` atau `1`.

Secara sederhana, alurnya seperti ini:

```text
Data
  |
  v
01101000
  |
  v
Mapping bit -> frekuensi
  |
  v
1000 -> 2000 -> 2000 -> 1000 -> ...
  |
  v
HDMI Audio
  |
  v
Receiver
  |
  v
Analisis frekuensi
  |
  v
0 1 1 0 1 0 0 0
```

Untuk sekarang, kita belum terlalu memikirkan masalah seperti **kecepatan transfer, sinkronisasi, error correction, noise, framing**, dan sebagainya.

Target tahap ini sederhana dulu:

> **Apakah kita benar-benar bisa mengirim dan menerima bit melalui audio HDMI?**

Kalau bagian dasar ini berhasil, barulah eksperimennya bisa dikembangkan lebih jauh.

## Mengecek Kemampuan Audio HDMI

Sebelum mulai mengirim data, gw perlu mengetahui dulu kemampuan hardware yang digunakan.

Hal pertama yang dicek adalah perangkat audio HDMI yang tersedia dan format audio yang bisa digunakan.

### Laptop / PC A (Sender)

Di sisi sender, `aplay -l` digunakan untuk melihat daftar perangkat playback yang tersedia:

```sh
[laptop1@kevinadhaikal ~]$ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: Generic [HD-Audio Generic], device 3: HDMI 0 [HDMI 0]
Subdevices: 1/1
Subdevice #0: subdevice #0
card 0: Generic [HD-Audio Generic], device 7: HDMI 1 [MACROSILICON]
Subdevices: 1/1
Subdevice #0: subdevice #0
card 1: Generic_1 [HD-Audio Generic], device 0: ALC257 Analog [ALC257 Analog]
Subdevices: 1/1
Subdevice #0: subdevice #0
```

Dari sini terlihat bahwa terdapat beberapa perangkat audio, termasuk output HDMI.

Untuk eksperimen ini, perangkat yang digunakan adalah:

```text
hw:0,7
```

Kemudian kemampuan hardware-nya dicek menggunakan:

```sh
aplay -D hw:0,7 --dump-hw-params /dev/zero
```

Hasilnya:

```text
Playing raw data '/dev/zero' : Unsigned 8 bit, Rate 8000 Hz, Mono
HW Params of device "hw:0,7":
--------------------
ACCESS: MMAP_INTERLEAVED RW_INTERLEAVED
FORMAT: S16_LE S32_LE
SUBFORMAT: STD MSBITS_MAX
SAMPLE_BITS: [16 32]
FRAME_BITS: [32 256]
CHANNELS: [2 8]
RATE: [32000 192000]
PERIOD_TIME: (20 16384000]
PERIOD_SIZE: [4 524288]
PERIOD_BYTES: [128 2097152]
PERIODS: [2 32]
BUFFER_TIME: (41 32768000]
BUFFER_SIZE: [8 1048576]
BUFFER_BYTES: [128 4194304]
TICK_TIME: ALL
--------------------
aplay: set_params:1393: Sample format non available
Available formats:
- S16_LE
- S32_LE
```

Ada beberapa informasi menarik dari hasil tersebut.

Perangkat HDMI ini mendukung:

* `S16_LE`
* `S32_LE`
* 2 sampai 8 channel
* sample rate dari `32000` sampai `192000 Hz`

### Laptop / PC B (Receiver)

Selanjutnya kita cek perangkat capture pada laptop penerima.

Untuk melihat perangkat recording yang tersedia, digunakan:

```sh
[laptop2@kevinadhaikal ~]$ arecord -l
**** List of CAPTURE Hardware Devices ****
card 1: Generic_1 [HD-Audio Generic], device 0: ALC257 Analog [ALC257 Analog]
Subdevices: 1/1
Subdevice #0: subdevice #0
card 2: acp [acp], device 0: DMIC capture dmic-hifi-0 []
Subdevices: 1/1
Subdevice #0: subdevice #0
card 3: MS2109 [MS2109], device 0: USB Audio [USB Audio]
Subdevices: 1/1
Subdevice #0: subdevice #0
```

Pada laptop ini, audio HDMI yang masuk diterima melalui USB HDMI capture device berbasis `MS2109`.

Device yang digunakan adalah:

```text
hw:3,0
```

Kemudian kemampuan capture device dicek menggunakan:

```sh
arecord -D hw:3,0 --dump-hw-params /dev/null
```

Hasilnya:

```text
Warning: Some sources (like microphones) may produce inaudible results
         with 8-bit sampling. Use '-f' argument to increase resolution
         e.g. '-f S16_LE'.
HW Params of device "hw:3,0":
--------------------
ACCESS: MMAP_INTERLEAVED
FORMAT: S16_LE
SUBFORMAT: STD MSBITS_MAX
SAMPLE_BITS: 16
FRAME_BITS: 32
CHANNELS: 2
RATE: 48000
PERIOD_TIME: [1000 1000000]
PERIOD_SIZE: [48 48000]
PERIOD_BYTES: [192 192000]
PERIODS: [2 1024]
BUFFER_TIME: [2000 2000000]
BUFFER_SIZE: [96 96000]
BUFFER_BYTES: [384 384000]
TICK_TIME: ALL
--------------------
arecord: set_params:1393: Sample format non available
Available formats:
- S16_LE
```

Nah, kalau kita liat dari hasil tersebut, receiver hanya bisa

```text
Format       : S16_LE
Sample rate  : 48000 Hz
Channel      : 2 (stereo)
```

Jadi, karena Receiver hanya bisa menerima dengan hasil tersebut, Sender juga harus sepakat bahwa Sender mengirim dengan sesuai hasil Receiver tersebut.

---

Tetapi, pengen coba dari yang gampang dulu. jadi kita sepakat dulu bahwa
```text
Format       : S16_LE
Sample rate  : 48000 Hz
Channel      : 1 (Mono)
```
Yes. Mono. kita ngelakuin satu channel dulu.

Oke, langsung tanpa basa-basi, kita langsung eksekusi

## Membuat Encoder

Seperti yang gw bilang, kita akan menggunakan **Frequency Shift Keying (FSK)**. dan saya sudah membuat code nya itu ada di [1_generate_wave.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_1/1_generate_wave.py) untuk melihat hasil generate bit "0" dan "1" jadi suara, dan per bit itu, saya buat 100ms per bit.

setelah menjalankan code pythonnya, nanti akan memberikan file bernama `output.wav`. kita cek menggunakan aplikasi Audacity, dan ubah menjadi Spectogram. dan nanti hasilnya seperti gambar dibawah ini.

<img width="1092" height="565" alt="1_spectogram" src="https://github.com/hmif-unm/hdmi-file-transfer/blob/main/assets/audio/tahap_1/1_spectogram.png?raw=true" />

nah, kalo lu bisa liat di gambar itu, disitu menghasilkan audio sepanjang 200ms (0.2 detik). di 100ms awal itu menghasilkan 1000hz, dan 100ms selanjutnya menghasilkan 2000hz.

Nah, sebelumnya kita sudah menentukan mapping antara bit dan frekuensi seperti ini:

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

Jadi, dari frekuensi yang kita hasilkan:

1000 Hz → 0
2000 Hz → 1

Maka audio tersebut merepresentasikan data biner:
```text
01
```
Jadi sebenarnya kita bukan mengubah audio menjadi biner secara langsung, tetapi kita menggunakan frekuensi tertentu sebagai representasi dari bit.

## Membuat Decoder

Karena kita sudah membuat Encoder dan menghasilkan file bernama `output.wav`, sekarang kita akan membuat **Decoder**.

Kalau di Encoder kita mengubah bit menjadi sine wave dengan frekuensi tertentu, maka di Decoder kita melakukan kebalikannya: membaca file `.wav`, menganalisis sinyalnya, lalu menentukan bit berdasarkan frekuensi yang paling cocok.

Karena sebelumnya kita sudah menentukan mapping:

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

maka Decoder perlu mengecek, dari setiap potongan audio, apakah sinyal tersebut lebih cocok dengan **1000 Hz** atau **2000 Hz**. Saya sudah membuat code-nya di file [2_decode_wave.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_1/2_decode_wave.py).

Bagian code yang akan kita highlight adalah:

```py
...
wave_0 = np.sin(2 * np.pi * FREQ_0 * t)
wave_1 = np.sin(2 * np.pi * FREQ_1 * t)

score_0 = np.sum(samples * wave_0)
score_1 = np.sum(samples * wave_1)

if score_0 > score_1:
    decoded_bits += "0"
else:
    decoded_bits += "1"
```

Nah, bagian `wave_0` dan `wave_1` digunakan untuk **membuat sine wave referensi** berdasarkan frekuensi yang sudah kita sepakati sebelumnya.

Jadi:

```py
wave_0 = np.sin(2 * np.pi * FREQ_0 * t)
```

akan membuat sine wave dengan frekuensi **1000 Hz**, sedangkan:

```py
wave_1 = np.sin(2 * np.pi * FREQ_1 * t)
```

akan membuat sine wave dengan frekuensi **2000 Hz**.

Setelah itu, kita ingin mengetahui sinyal yang ada di `samples` lebih cocok dengan sine wave 1000 Hz atau 2000 Hz.

Untuk melakukan itu, kita menghitung `score`:

```py
score_0 = np.sum(samples * wave_0)
score_1 = np.sum(samples * wave_1)
```

Secara sederhana, kita mengalikan sample audio yang diterima dengan sine wave referensi, lalu menjumlahkan hasilnya menggunakan `np.sum()`.

Semakin besar nilai `score`, berarti sinyal yang diterima semakin **cocok** dengan frekuensi tersebut.

Jadi kalau hasilnya misalnya:

```text
score_0 = 150000000
score_1 = 2000000
```

berarti sinyalnya jauh lebih cocok dengan **1000 Hz**, sehingga kita anggap sebagai bit `0`.

Sebaliknya, kalau:

```text
score_0 = 1000000
score_1 = 140000000
```

berarti sinyalnya lebih cocok dengan **2000 Hz**, sehingga kita anggap sebagai bit `1`.

Makanya kita punya kondisi:

```py
if score_0 > score_1:
    decoded_bits += "0"
else:
    decoded_bits += "1"
```

Kalau `score_0` lebih besar, kita mendapatkan `0`. Kalau `score_1` lebih besar, kita mendapatkan `1`.

Sekarang kita coba jalankan code Python-nya:

```text
[laptop1@kevinadhaikal tahap_1]$ python 2_decode_wave.py
Decoded: 01
```

Dan akhirnya, kita berhasil **mengembalikan sine wave yang ada di file `output.wav` menjadi bit `01`**.

Kita sudah berhasil membuat komunikasi data sederhana menggunakan **frekuensi audio sebagai representasi bit**.
