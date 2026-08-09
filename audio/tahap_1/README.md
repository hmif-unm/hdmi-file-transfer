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

# Mengecek Kemampuan Audio HDMI

Sebelum mulai mengirim data, gw perlu mengetahui dulu kemampuan hardware yang digunakan.

Hal pertama yang dicek adalah perangkat audio HDMI yang tersedia dan format audio yang bisa digunakan.

## Laptop / PC A (Sender)

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

# Laptop / PC B (Receiver)

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
