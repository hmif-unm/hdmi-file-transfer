# Tahap Pertama | Eksperimen Encoding dan Decoding Audio

Di tahap pertama ini, kita mulai dari hal yang paling sederhana: **mencoba mengubah data menjadi sinyal audio, kemudian mengembalikannya lagi menjadi data.**

Untuk percobaan awal, kita belum menggunakan perangkat komunikasi apa pun. Kita hanya menggunakan **file WAV** sebagai media untuk menguji apakah proses encoding dan decoding menggunakan sinyal audio dapat bekerja.

## Ide Dasar

Untuk merepresentasikan data menggunakan audio, kita membutuhkan suatu cara untuk mengubah bit menjadi sinyal yang bisa dibuat dan dianalisis kembali.

Untuk percobaan pertama, gw menggunakan teknik yang sangat sederhana: **Frequency Shift Keying (FSK)**.

Konsepnya cukup gampang. Setiap bit direpresentasikan menggunakan frekuensi tertentu:

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

Jadi, misalnya data yang ingin direpresentasikan adalah:

```text
01101000
```

Maka setiap bit akan diubah menjadi frekuensi:

```text
1000 Hz -> 2000 Hz -> 2000 Hz -> 1000 Hz
2000 Hz -> 1000 Hz -> 1000 Hz -> 1000 Hz
```

Di sisi encoder, program akan membuat sinyal audio berdasarkan urutan frekuensi tersebut dan menyimpannya ke dalam sebuah file `.wav`.

Kemudian di sisi decoder, file WAV tersebut akan dibaca dan dianalisis. Program akan mencari frekuensi yang paling cocok pada setiap bagian audio, kemudian menentukan apakah frekuensi tersebut merepresentasikan `0` atau `1`.

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
WAV File
  |
  v
Decoder
  |
  v
Analisis frekuensi
  |
  v
0 1 1 0 1 0 0 0
```

Untuk sekarang, kita belum terlalu memikirkan masalah seperti **kecepatan transfer, sinkronisasi, error correction, noise, framing**, dan sebagainya.

Target tahap ini sederhana dulu:

> **Apakah kita bisa mengubah bit menjadi sinyal audio, menyimpannya sebagai WAV, kemudian membaca kembali sinyal tersebut menjadi bit?**

Kalau bagian dasar ini berhasil, barulah kita bisa membawa konsep tersebut ke tahap berikutnya.

## Membuat Encoder

Seperti yang gw bilang, kita akan menggunakan **Frequency Shift Keying (FSK)**. dan saya sudah membuat code nya itu ada di 1_generate_wave.py untuk melihat hasil generate bit "0" dan "1" jadi suara, dan per bit itu, saya buat 100ms per bit.

setelah menjalankan code pythonnya, nanti akan memberikan file bernama `output.wav`. kita cek menggunakan aplikasi Audacity, dan ubah menjadi Spectogram. dan nanti hasilnya seperti gambar dibawah ini.

<img alt="1_spectogram" src="https://github.com/hmif-unm/hdmi-file-transfer/blob/main/assets/audio/tahap_1/1_spectogram.png?raw=true" />

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

Nah, sekarang kita kan ga mungkin untuk ngeliat Spectogram, dan kita menulis sendiri binernya, kan? nah, sekarang kita membuat Decoder nya.

## Membuat Decoder

Karena kita sudah membuat Encoder dan menghasilkan file bernama `output.wav`, sekarang kita akan membuat **Decoder**.

Kalau di Encoder kita mengubah bit menjadi sine wave dengan frekuensi tertentu, maka di Decoder kita melakukan kebalikannya: membaca file `.wav`, menganalisis sinyalnya, lalu menentukan bit berdasarkan frekuensi yang paling cocok.

Karena sebelumnya kita sudah menentukan mapping:

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

maka Decoder perlu mengecek, dari setiap potongan audio, apakah sinyal tersebut lebih cocok dengan **1000 Hz** atau **2000 Hz**.

Saya sudah membuat code-nya di file [2_decode_wave.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_1/2_decode_wave.py)

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

Kalau `score_0` lebih besar, kita mendapatkan `0`.

Kalau `score_1` lebih besar, kita mendapatkan `1`.

Sekarang kita coba jalankan code Python-nya:

```text
[laptop1@kevinadhaikal tahap_1]$ python 2_decode_wave.py
Decoded: 01
```

Dan akhirnya, kita berhasil **mengembalikan sine wave yang ada di file `output.wav` menjadi bit `01`**.

Jadi alurnya sekarang sudah lengkap:

```text
Bit
 ↓
Encoder
 ↓
Sine Wave
 ↓
output.wav
 ↓
Decoder
 ↓
Bit
```

Kita sudah berhasil membuat komunikasi data sederhana menggunakan **frekuensi audio sebagai representasi bit**.

## Mengirim / Menerima Text

Nah, kita sudah berhasil membuat Encoder dari sebuah bit, menjadi audio. dan kita juga sudah berhasil membuat Decoder dari sebuah audio ke bit. Sekarang, kita pengen membuat transfer dalam bentuk text.

Untuk di sisi encoder nya, kita hanya perlu melakukan convert text menjadi sebuah biner, dan mengirimkannya ke decoder. dan disisi decoder hanya perlu mengumpulkan bitnya, dan di convert dari bit ke text.

Saya juga udah buat file nya. [3_encode_text.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_1/3_encode_text.py) dan [4_decode_text.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_1/4_decode_text.py). dan sekarang kita coba encode text "hello world", dan kita akan coba mendecode.

```text
[laptop1@kevinadhaikal tahap_1]$ python 3_encode_text.py 
Masukkan text: hello world 
file disimpan menjadi output.wav
[laptop1@kevinadhaikal tahap_1]$ python 4_decode_text.py 
decoded: hello world
[laptop1@kevinadhaikal tahap_1]$ 
```
Dan hasil Spectogramnya seperti ini

<img alt="2_hello_world_spectogram" src="https://github.com/hmif-unm/hdmi-file-transfer/blob/main/assets/audio/tahap_1/2_hello_world_spectogram.png?raw=true" />

## Kesimpulan

Dari percobaan ini, kita sudah berhasil membuat alur sederhana untuk mengubah data menjadi sinyal audio dan mengembalikannya lagi menjadi data.

Mulai dari:

```text
Bit
 ↓
FSK
 ↓
Sinyal Audio
 ↓
WAV
 ↓
Decoder
 ↓
Bit
```

Kemudian kita kembangkan lagi supaya bisa mengirim **text**, sehingga alurnya menjadi:

```text
Text
 ↓
Binary
 ↓
FSK
 ↓
Audio
 ↓
WAV
 ↓
Decoder
 ↓
Binary
 ↓
Text
```

Dan percobaan tersebut berhasil. Text `hello world` yang dimasukkan ke encoder berhasil dibaca kembali oleh decoder sebagai `hello world`.

Jadi, dari tahap ini kita sudah membuktikan bahwa **data bisa direpresentasikan menggunakan frekuensi audio**, kemudian sinyal tersebut bisa dianalisis kembali untuk mendapatkan data aslinya.

Tapi ada satu masalah: Sampai tahap ini, kita masih menggunakan **file WAV sebagai media perantara**.

Artinya, prosesnya masih seperti:

```text
Encoder
   |
   v
output.wav
   |
   v
Decoder
```

Belum ada proses pengiriman data secara langsung.

Nah, dari sini muncul pertanyaan berikutnya:

> **"Kalau audio tersebut tidak disimpan sebagai file, tapi langsung dikirim melalui suatu koneksi, apakah datanya masih bisa diterima dan di-decode dengan benar?"**

Dan di sinilah kita masuk ke [tahap berikutnya](https://github.com/hmif-unm/hdmi-file-transfer/tree/main/audio/tahap_2).
