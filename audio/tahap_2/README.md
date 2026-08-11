# Tahap Kedua | Mengirim Pesan lewat HDMI

Di tahap kedua ini, gw mulai mencoba mengirim pesan melalui HDMI.

Di tahap pertama, gw sudah mencoba bagaimana cara mengubah bit menjadi sinyal audio, kemudian mengembangkan lagi sampai text bisa diubah menjadi audio. Setelah itu, gw juga membuat decoder untuk membaca kembali audio tersebut dan mengubahnya menjadi data.

Jadi, bagian dasar untuk mengubah data menjadi audio dan membacanya kembali sudah berhasil.

Nah, sekarang muncul pertanyaan berikutnya:

> **"Kalau proses encode dan decode-nya sudah berhasil, apakah audio tersebut bisa kita kirim melalui HDMI?"**

Dari sini, gw mulai mencoba menggunakan **jalur audio HDMI** sebagai media pengiriman data.

## Dari Audio ke HDMI

Di tahap sebelumnya, kita sudah berhasil membuat audio yang membawa data. Sekarang gw mau mencoba mengirim audio tersebut melalui HDMI.

Untuk teknik pengirimannya, gw masih menggunakan **Frequency Shift Keying (FSK)** yang sudah dibuat dan diuji di tahap sebelumnya. Jadi di tahap ini gw nggak perlu mengulang lagi bagaimana bit atau text diubah menjadi frekuensi.

Yang berubah sekarang adalah **medianya**.

Kalau sebelumnya alurnya kurang lebih seperti:

```text
Text
  |
  v
Encoder
  |
  v
Audio
  |
  v
Decoder
  |
  v
Text
```

Sekarang gw mau mencoba memasukkan HDMI ke dalam proses tersebut:

```text
Text
  |
  v
Encoder
  |
  v
Audio
  |
  v
HDMI
  |
  v
Receiver
  |
  v
Decoder
  |
  v
Text
```

Jadi intinya, encoder dan decoder yang sudah dibuat di tahap sebelumnya tetap digunakan. Kali ini gw cuma mau melihat apakah **sinyal audio hasil encoder bisa dikirim melalui HDMI dan diterima kembali dengan benar**.

Untuk sekarang, gw belum terlalu mikirin masalah seperti **kecepatan transfer, sinkronisasi, error correction, noise, framing**, dan sebagainya.

Target tahap ini sederhana dulu:

> **Apakah kita benar-benar bisa mengirim dan menerima data melalui audio HDMI?**

Kalau bagian dasarnya sudah berhasil, baru nanti kita coba kembangkan lagi.

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

Oke, langsung tanpa basa-basi, kita langsung eksekusi!

## Membuat Sender

sekarang kita coba mengirim data tersebut melalui jalur audio HDMI.

Untuk itu, kita membuat program **Sender** yang bertugas mengubah data menjadi sinyal audio, kemudian mengirimkannya melalui perangkat HDMI.

Data yang dikirim masih menggunakan konsep yang sama seperti tahap sebelumnya. Setiap bit direpresentasikan menggunakan frekuensi yang berbeda:

* `0` → 1000 Hz
* `1` → 2000 Hz

Jadi, tugas Sender kurang lebih adalah:

```text
Data
 ↓
Bit
 ↓
Frekuensi
 ↓
Sinyal Audio
 ↓
HDMI
```

Untuk codenya, sudah Saya buatin di file 1_sender_mono.py

Program Sender inilah yang nantinya menjalankan proses tersebut secara langsung, bukan lagi menyimpan hasilnya ke file WAV seperti pada tahap pertama.

## Membuat Receiver

Setelah Sender selesai dibuat, kita membutuhkan program yang melakukan kebalikannya, yaitu **Receiver**.

Receiver membaca audio yang masuk dari HDMI, kemudian mencoba menentukan frekuensi yang sedang diterima. Dari frekuensi tersebut, Receiver dapat mengetahui bit yang dikirim oleh Sender.

Karena kita menggunakan dua frekuensi, prosesnya sederhana:

```text
1000 Hz → 0
2000 Hz → 1
```

Secara sederhana prosesnya seperti ini:

```text
HDMI Audio
    ↓
Baca sample audio
    ↓
Analisis frekuensi
    ↓
1000 Hz / 2000 Hz
    ↓
0 / 1
    ↓
Cari Preamble
    ↓
Baca Data
    ↓
Bit → Byte → Teks
```

Untuk mendeteksi frekuensi, kita menggunakan korelasi terhadap gelombang sinus dan cosinus pada frekuensi yang sudah ditentukan.

Untuk codenya, sudah Saya buatin di file 2_receiver_mono.py

## Percobaan Mengirim dan Menerima Text

Oke, karena kita sudah membuat Sender dan Receiver, sekarang mari kita coba!

- Percobaan Pertama
  - PC / Laptop A
    ```text
    [laptop1@kevinadhaikal tahap_2]$ python 1_sender_mono.py
    Masukkan pesan: hello world 
    Mengirim...
    Selesai dikirim.
    ```

  - PC / Laptop B
    ```text
    [laptop2@kevinadhaikal tahap_2]$ python 2_receiver_mono.py 
    menunggu data...
    mendapatkan bits: 0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100
    isi message: 'hello world'
    ```
  
  Wah, ternyata kita berhasil transfer file lewat Audio HDMI! Mari kita coba lagi

- Percobaan Kedua
  - PC / Laptop A
    ```text
    [laptop1@kevinadhaikal tahap_2]$ python 1_sender_mono.py
    Masukkan pesan: hello world 
    Mengirim...
    Selesai dikirim.
    ```

  - PC / Laptop B
    ```text
    [laptop2@kevinadhaikal tahap_2]$ python 2_receiver_mono.py 
    menunggu data...
    mendapatkan bits: 00110100001100101011011000110110001101111001000000111011101101111011100100110110001100100
    isi message: '42¶67\x90;·¹62'
    ```
  
  Loh...? kok begini?

Percobaan pertama, memanglah berhasil. tapi saat mencoba kedua kalinya, tiba tiba data nya menjadi acak acakan. Mengapa bisa kayak gini ya?

## Mencari Solusi dan Memperbaiki

Hmmmmm... Mari kita lihat bit hasil pertama dan kedua

- Hasil Pertama
  ```
  0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100
  ```

- Hasil Kedua
  ```
  00110100001100101011011000110110001101111001000000111011101101111011100100110110001100100
  ```

Kalo kita teliti... Hasil kedua ini malah menambahkan `0` di bagian awalnya. Hmmmmm... mengapa itu bisa terjadi?

Ternyata, ini masalah timing dan sinkronisasi. Jadi gini:

- Disisi Sender:
  Setiap bit dikirim dalam 480 sample
  ```text
  |--------480--------|--------480--------|--------480--------|
        BIT 0               BIT 1               BIT 2
  ```

- Disisi Receiver:
  Pembacaan audio belum tentu dimulai tepat di awal sebuah bit
  ```text
  |--------480--------|--------480--------|--------480--------|
       ↑
     offset
  ```

Nah, jadi Receiver bisa saja mulai membaca beberapa sample lebih awal atau lebih lambat dari posisi sebenarnya. Karena Receiver selalu membagi data menjadi **480 sample per bit**, offset kecil ini akan membuat seluruh pembagian bit ikut bergeser.

Misalnya, Sender mengirim:

```text
BIT 0 | BIT 1 | BIT 2 | BIT 3 | ...
```

tetapi Receiver mulai membacanya sedikit lebih awal:

```text
  offset
    ↓
...| BIT 0 | BIT 1 | BIT 2 | BIT 3 | ...
```

Receiver akhirnya menganggap potongan audio yang bukan merupakan awal `BIT 0` sebagai awal data. Inilah yang menyebabkan munculnya `0` tambahan di bagian awal dan membuat seluruh bit setelahnya ikut bergeser.

Jadi, masalahnya bukan pada encoding atau correlation yang kita gunakan. Masalahnya adalah Receiver belum mengetahui secara pasti dimana posisi awal setiap bit berada.

Nah, untuk ngatasinnya... kita bisa melakukan mengirim preamble terlebih dahulu. jadi, preamble ini bisa dibilang kayak verifikasi dulu. setelah preamble, baru kirim data nya. nanti data nya berbentuk seperti ini

```text
PREAMBLE + DATA
```

dan di receiver nya juga harus mengecek preamble dulu. jika preamble nya valid, baru menerima datanya.

dan untuk preamblenya, saya buat seperti ini `1010101010101010`. ya. 2 byte (16 bit).  saya sudah revisi code nya di file 3_sender_mono.py dan 4_receiver_mono.py.

Sekarang, mari kita coba

- Percobaan Pertama
  - PC / Laptop A
    ```
    [laptop1@kevinadhaikal tahap_2]$ python 3_sender_mono.py 
    Masukkan pesan: hello world 
    Mengirim...
    Selesai dikirim.
    ```
  = PC / Laptop B
    ```
    [laptop2@kevinadhaikal tahap_2]$ python 4_receiver_mono.py 
    menunggu data...
    dapet preamble!
    mendapatkan bits: 01101000011001010110110001101100011011110010000001110111011011110111001001101100011001000
    isi message: 'hello world'
    ```

Oke... untuk percobaan pertama ini berhasil. sekarang kita melakukan percobaan kedua

- Percobaan Kedua
  - PC / Laptop A
    ```
    [laptop1@kevinadhaikal tahap_2]$ python 3_sender_mono.py 
    Masukkan pesan: hello world 
    Mengirim...
    Selesai dikirim.
    ```
  - PC / Laptop B
    ```
    [laptop2@kevinadhaikal tahap_2]$ python 4_receiver_mono.py 
    menunggu data...
    dapet preamble!
    mendapatkan bits: 01101000011001010110110001101100011011110010000001110111011011110111001001101100011001000
    isi message: 'hello world'
    ```

AKHIR NYA BERHASIL JUGA!