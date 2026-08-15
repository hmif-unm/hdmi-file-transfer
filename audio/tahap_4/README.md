# Tahap Keempat | Optimize Transfer File

Di tahap sebelumnya, kita sudah berhasil transfer file menggunakan audio HDMI. tetapi, itu membutuhkan waktu 22.08 detik hanya transfer file sebesar 256 byte.

Di tahap ini, Saya akan optimize Transfer File.

Tanpa basa-basi, kita langsung eksekusi saja.

## Mengubah Mono ke Stereo

Ini salah satu tahap yang bagus, karena ini akan memanfaatkan 2 Channel (Left and Right).

Kalo kita hitung:
```
Diketahui:
preamble = 16 bit (2 byte)
header = 144 bit (18 byte)
data = 2048 bit (256 byte)

bit per detik = 0.01 detik

Ditanya: berapa waktu nya?

Jawab:
bits = 16 + 144 + 2048
bits = 2208

waktu = (bits / channel) * bit_per_detik
waktu = (2208 / 2) * 0.01
waktu = 1104 * 0.01
waktu = 11.04
```

Membutuhkan 11.04 detik, dan ini lumayan lah ya.

Untuk bagian code nya, kita masih pake menggunakan sender dan receiver mono, dan kita hanya perlu modif bagian

- Channels (di jadiin 2 channels)
  Untuk dibagian Sender dan di Receiver, kita harus mengubah dari `CHANNELS = 1` menjadi `CHANNELS = 2`.

- Modulate dibikin jadi 2 channels (Sender)
  di bagian function `modulate()`, sebelumnya bentukannya begini
  
	```py
	def modulate(bits):
		output = []
		for bit in bits:
			if bit == "0": output.append(tone(FREQ_0, BIT_TIME))
			else: output.append(tone(FREQ_1, BIT_TIME))
		return np.concatenate(output)
  ```

	nah, kalo kita liat code ini, ini hanya 1 channel saja. dia memberikan tone hanya di satu channel saja, dan append ke output.

	sekarang, kita buat 2 channel (left dan right), menjadi seperti ini

	```py
	def modulate(bits):
		output = []
		for i in range(0, len(bits), 2):
			left_bit = bits[i]
			right_bit = bits[i + 1]
			left = tone(FREQ_0 if left_bit == "0" else FREQ_1, BIT_TIME)
			right = tone(FREQ_0 if right_bit == "0" else FREQ_1, BIT_TIME)
			stereo = np.column_stack((left, right))
			output.append(stereo)
		return np.concatenate(output)
	```

	Nah, kalo kita lihat-lihat dari code ini, ini akan menghandle 2 bit dalam 0.01 detik. jadi, left nya itu ngehandle bit pertama, right nya itu ngehandle bit yang kedua. jadi, nanti akan mengirim 2 bit dalam 0.01 detik.

- Membaca bit menjadi 2 channel (Receiver)
	Sekarang, kita ke code Receiver.

	Kita sudah mempunyau function `detect_bit()`. tetapi ini hanya cuma 1 Channel doang. tidak bisa mengambil data Left Channel dan Right Channel. jadi kita akan membuat function `detect_bits_stereo()` agar bisa memproses 2 bits dalam 0.01 detik.

	```py
	def detect_bits_stereo(stereo_chunk):
		left_ch = stereo_chunk[:, 0]
		right_ch = stereo_chunk[:, 1]
		left_bit = detect_bit(left_ch)
		right_bit = detect_bit(right_ch)
		return left_bit, right_bit
	```

Untuk codenya saya sudah modifikasi di file 1_sender_stereo.py dan 2_receiver_stereo.py.

Oke sekarang kita coba.

- PC / Laptop 1
	```text
	[laptop1@kevinadhaikal tahap_4]$ python 1_sender_stereo.py 256b.bin hw:1,7
	[LOG] Mengirim READY frekuensi agar tersinkron...
	[LOG] Selesai dikirim.
	```

- PC / Laptop 2
	```text
	[laptop2@kevinadhaikal tahap_4]$ python 2_receiver_stereo.py result.bin hw:0,0
	[LOG] Menunggu sender...
	[LOG] Sender ditemukan! sedang diproses...
	[LOG] Berhasil menerima semua buffer file! mengecek file...
	[LOG] Magic header sesuai!
	[LOG] Panjang file sesuai: 256 bytes
	[LOG] CRC32 Sesuai: 0xa188a0e5
	[LOG] File berhasil disimpan!
	```

Dan kita akhirnya berhasil membuat Transfer File lewat Audio HDMI dengan Stereo! jadi, transfer lumayan cepat. dari 22.08 detik ke 11.04 detik!

Tapi... keknya ini masih bisa dibilang lambat. Kita harus ganti teknik **Frequency Shift Keying (FSK)** ke yang lain, tapi apa ya? hmmmm...

## Mengganti Teknik

Ya. Kita harus mengganti teknik, karena teknik **Frequency Shift Keying (FSK)** ini bisa dibilang sangat lambat, karena per sample = 1 bit. dan saat kita membuat support 2 channel, dan hanya menghasilkan 2 bit per sample, dan ini sangat lambat. transfer file 256 byte harus membutuhkan waktu 11.04 detik. jadi kita harus ganti teknik.