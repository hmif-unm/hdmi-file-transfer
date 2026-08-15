# Tahap Ketiga | Transfer File

Di tahap ketiga ini, sekarang kita mulai mencoba untuk transfer file. Bukan cuma sebatas ngirim pesan doang, seperti di tahap kedua.

Jadi, nanti Sender nya mengirim file lewat frekuensi audio dengan teknik Frequency Shift Key (FSK). untuk FSK nya, seperti yang kita sepakati di tahap 1

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

Oke, tanpa basa-basi, kita langsung eksekusi aja.

## Membuat Sender

Karena kita sudah mempunyai file sender sebelumnya, kita tinggal menambahkan beberapa bagian agar sender bisa mengirim **file**, bukan hanya message biasa.

Bagian yang perlu dibuat:

- Membuat Header
- Membaca file
- CRC Hash

untuk file code nya, sudah saya buat di [1_sender_mono.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_3/1_sender_mono.py)

---

- ### Membuat Header

    Kita harus membuat header agar receiver tahu informasi dasar dari file yang akan dikirim.

    Header ini nantinya dikirim sebelum isi file.

    Informasi yang bisa dimasukkan ke dalam header antara lain:

    * Nama file
    * Ukuran file
    * CRC
    * Dan informasi lain yang dibutuhkan receiver

    Saya akan mendesain header nya seperti ini:

    ```text
    +------------------+------------------------+----------------+
    | MAGIC            | FILE_SIZE              | CRC32          |
    | HDMItA (6 bytes) | 8 bytes                | 4 bytes        |
    +------------------+------------------------+----------------+
    ```

    Receiver akan membaca bagian header terlebih dahulu. Setelah header berhasil dibaca, receiver bisa mengetahui berapa banyak data yang harus diterima dan bagaimana data tersebut harus disimpan.

    Dengan begitu, receiver tidak perlu menebak-nebak kapan file selesai dikirim.

- ### Membaca File

    Setelah header dibuat, kita perlu membaca isi file yang ingin dikirim.

    Karena file tidak selalu berupa text, kita **tidak boleh membaca file menggunakan mode text**.

    File harus dibaca dalam bentuk `bytes`.

    Contohnya:

    ```python
    with open(filename, "rb") as f:
        data = f.read()
    ```

    Dengan menggunakan `"rb"`, isi file akan dibaca sebagai kumpulan byte.

    Misalnya file memiliki isi:

    ```text
    48 65 6C 6C 6F
    ```

    Maka data tersebut tetap dianggap sebagai:

    ```python
    b"Hello"
    ```

    bukan sebagai string biasa.

- ### CRC Hash

    Setelah mendapatkan data file, kita juga perlu membuat CRC.

    CRC digunakan oleh receiver untuk mengecek apakah data yang diterima sama dengan data yang dikirim.

    Receiver kemudian menghitung CRC dari data yang diterima.

    Jika hasilnya sama dengan CRC yang dikirim oleh sender:

    ```text
    CRC Sender == CRC Receiver
    ```

    maka data dianggap berhasil diterima tanpa error.

    Jika berbeda:

    ```text
    CRC Sender != CRC Receiver
    ```

    berarti kemungkinan terdapat data yang berubah atau rusak selama proses transfer.

## Membuat Receiver

Karena kita sudah mempunyai file receiver sebelumnya, kita tinggal menambahkan beberapa bagian agar receiver dapat menerima dan menyimpan file yang dikirim oleh sender.

Bagian yang perlu dibuat:

* Membaca Header
* Menerima data file
* Menulis file
* Validasi CRC32 Hash

untuk file code nya, sudah saya buat di [2_receiver_mono.py](https://github.com/hmif-unm/hdmi-file-transfer/blob/main/audio/tahap_3/2_receiver_mono.py)

---

- ### Membaca Header

    Receiver akan membaca header yang dikirim oleh sender sebelum menerima isi file.

    Header memiliki ukuran **18 bytes** dengan format:

    ```text
    +------------------+------------------------+----------------+
    | MAGIC            | FILE_SIZE              | CRC32          |
    | HDMItA (6 bytes) | 8 bytes                | 4 bytes        |
    +------------------+------------------------+----------------+
    ```

    Kemudian header dipisahkan menjadi:

    ```text
    MAGIC     = HDMItA (6 bytes)
    FILE_SIZE = 8 bytes
    CRC32     = 4 bytes
    ```

- ### Menerima Data File

    Setelah header berhasil dibaca, receiver mulai menerima data file. Dan juga, receiver akan terus menerima data sampai jumlah byte yang diterima sama dengan `FILE_SIZE`.

    Contohnya jika:

    ```text
    FILE_SIZE = 1024
    ```

    maka receiver harus menerima:

    ```text
    1024 bytes
    ```

- ### Menulis File

    Setelah data file berhasil diterima, data tersebut kemudian ditulis ke file menggunakan mode binary.

    ```python
    with open(filename, "wb") as f:
        f.write(file_data)
    ```

    Mode `"wb"` digunakan karena file yang ditransfer dapat berupa file binary.

- ### Validasi CRC32 Hash

    Setelah seluruh file diterima, receiver akan menggunakan nilai CRC32 yang terdapat pada header. Receiver kemudian menghitung CRC32 dari data file yang telah diterima.

    Jika:

    ```text
    CRC Sender == CRC Receiver
    ```

    maka data dianggap berhasil diterima tanpa adanya perubahan.

    Sebaliknya, jika:

    ```text
    CRC Sender == CRC Receiver
    ```

    maka terdapat kemungkinan data mengalami error selama proses transfer.

## Percobaan Pertama

Oke, sekarang kita coba melakukan transfer file lewat HDMI, dan kita akan mengirim file berisi random bytes, dan dengan panjang 256 byte.

karena saya di Linux, saya membuat file random bytes dengan panjang 256 bit menggunakan `dd` di PC / Laptop A:

```
dd if=/dev/urandom of=256b.bin bs=128 count=2 status=progress
```

---

- PC / Laptop A
  ```text
  [laptop1@kevinadhaikal tahap_3]$ python 1_sender_mono.py 256b.bin hw:0,7
  [LOG] Mengirim READY frekuensi agar tersinkron...
  [LOG] Selesai dikirim.
  ```
- PC / Laptop B
  ```text
  [laptop2@kevinadhaikal tahap_3]$ python 2_receiver_mono.py save.bin hw:2,0
  [LOG] Menunggu sender...
  [LOG] Sender ditemukan! sedang diproses...
  [LOG] Berhasil menerima semua buffer file! mengecek file...
  [LOG] Panjang file sesuai: 256 bytes
  [LOG] CRC32 Sesuai: 0xa188a0e5
  [LOG] File berhasil di simpan!
  ```

Wah, ternyata berhasil! Tetapi... hanya transfer file 256 byte aja kok lama banget ya? hmmmmm...

Jika kita hitung-hitung...

```
preamble = 16 bit (2 byte)
header = 144 bit (18 byte)
data = 2048 bit (256 byte)

16 + 144 + 2048 = 2208 bits
2208 * 0.01 = 22.08 detik
```

Wah... 22.08 detik!? cuma 256 byte doang!? lama banget.

## Kesimpulan

Pada tahap ketiga ini, kita sudah berhasil mengembangkan sistem dari yang sebelumnya hanya dapat mengirim pesan menjadi **transfer file melalui HDMI Audio**.

File dikirim dalam bentuk data binary menggunakan teknik **Frequency Shift Keying (FSK)**, dengan pemetaan:

| Bit | Frekuensi |
| --- | --------- |
| `0` | 1000 Hz   |
| `1` | 2000 Hz   |

Sebelum data file dikirim, Sender mengirimkan **preamble** untuk sinkronisasi, kemudian dilanjutkan dengan **header** yang berisi ukuran file dan CRC32. Setelah itu, isi file dikirim sebagai binary data.

Pada sisi Receiver, header digunakan untuk mengetahui ukuran file yang harus diterima. Setelah seluruh data diterima, Receiver menghitung kembali CRC32 dan membandingkannya dengan CRC32 yang dikirim oleh Sender.

Pada percobaan pertama, sistem berhasil mentransfer file random berukuran **256 bytes** dari satu komputer ke komputer lainnya melalui HDMI Audio. File yang diterima memiliki ukuran yang sesuai dan nilai CRC32 yang sama dengan file asli.

Namun, dari percobaan tersebut juga terlihat bahwa sistem masih memiliki **kecepatan transfer yang sangat rendah**. Dengan `BIT_TIME = 0.01` detik, satu bit membutuhkan waktu 10 ms. Untuk mengirim 256 bytes saja, total waktu teoritisnya mencapai sekitar **22.08 detik**, belum termasuk waktu tambahan dari proses sinkronisasi dan pemrosesan.

Artinya, sistem yang dibuat pada tahap ini sudah berhasil membuktikan bahwa **data file dapat ditransfer melalui HDMI Audio**, tetapi performanya masih jauh dari optimal.

Hal ini menjadi dasar untuk tahap berikutnya, yaitu melakukan **optimasi kecepatan transfer**, misalnya dengan memperkecil waktu per bit, menggunakan teknik encoding yang lebih efisien, meningkatkan jumlah bit yang dapat dikirim dalam satu simbol, atau menggunakan teknik modulasi yang lebih kompleks.

Yuk, kita lanjut ke [Tahap Selanjutnya](https://github.com/hmif-unm/hdmi-file-transfer/tree/main/audio/tahap_4).
