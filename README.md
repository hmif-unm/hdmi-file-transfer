# File Transfer HDMI

> *"Apakah HDMI bisa jadi alat transfer file?"*

Riset ini berawal dari pertanyaan sederhana itu.

Gw, Kevin Adhaikal, penasaran apakah koneksi HDMI yang biasanya kita pakai buat ngirim gambar dan suara juga bisa dimanfaatin buat ngirim data lain, seperti file.

Daripada cuma kepikiran, akhirnya gw  untuk coba eksperimen.

Riset ini gw bagi menjadi dua bagian:

---
- `audio/`

   Eksperimen transfer file menggunakan **audio melalui HDMI** sebagai media transmisi.

   Di bagian ini, audio HDMI dimanfaatin untuk membawa data digital. Mulai dari percobaan sederhana seperti mengubah bit menjadi frekuensi, membaca kembali frekuensinya, sampai nantinya mencoba mengirim data yang lebih kompleks.

   ```text
   Computer
      │
      │ HDMI Audio
      ▼
   Receiver
      │
      ▼
   Binary Data
   ```

- `video/`

   Eksperimen transfer file menggunakan **video melalui HDMI** sebagai media transmisi.

   Konsepnya kurang lebih sama, tapi kali ini yang dimanfaatin adalah sinyal video. Data akan dicoba direpresentasikan ke dalam gambar/frame yang kemudian dikirim melalui HDMI dan dibaca kembali oleh receiver.

   ```text
   Computer
      │
      │ HDMI Video
      ▼
   Receiver
      │
      ▼
   Binary Data
   ```

## Tujuan

Tujuan utama riset ini bukan langsung bikin transfer file dengan kecepatan tinggi.

Gw lebih pengen cari tahu:

**Seberapa jauh HDMI bisa dimanfaatin sebagai media komunikasi data?**

Mulai dari hal yang paling sederhana, sampai kalau memungkinkan bisa berkembang menjadi transfer file yang benar-benar bisa digunakan.

Riset ini masih dalam tahap eksperimen dan hasilnya bisa berubah seiring percobaan berikutnya.

## Kebutuhan

- 2 buah PC/Lapotp
  - Laptop A
    - OS: Linux (Arch Linux)
    - Sebagai: Sender
  - Laptop B
    - OS: Linux (Arch Linux)
    - Sebagai: Receiver
- 1 buah HDMI Video Capture
- 1 buah HDMI

---

**Author:** Kevin Adhaikal