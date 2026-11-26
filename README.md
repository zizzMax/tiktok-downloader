# TikTok Downloader — Tempel Link, Keluar Semuanya

Kasih satu link postingan TikTok, keluar satu blok kecil berisi info + semua link download langsungnya. Videonya kualitas terbaik tanpa watermark (kualitas orisinal/HD), fotonya full-res, plus musik dan cover kalau ada.

## Persiapan

Butuh Python 3 dan satu library:

```bash
pip install requests
```

Kalau kena error `externally-managed-environment` (Debian/Ubuntu baru), pilih salah satu:

```bash
apt install python3-requests          # cara sistem
python3 -m venv venv && venv/bin/pip install requests   # cara venv
pip install --break-system-packages requests            # cara paksa
```

Di banyak sistem perintahnya `python3`, bukan `python` — contoh di bawah pakai `python3`.

## Cara menjalankan

### 1. Lihat info + link download

```bash
python3 tiktok.py "<link>"
```

Contoh untuk postingan video:

```
type      : video
pengupload: @0_0sshaa
caption   :

video        : https://dl.tiktokio.com/download?token=...
musik        : https://dl.tiktokio.com/download?token=...
cover        : https://p16-common-sign.tiktokcdn-us.com/...
```

Contoh untuk postingan foto (ada baris `jumlah` = banyaknya foto):

```
type      : photo
pengupload: @mrmarvelslideshow
caption   : This film will be amazing #avengersdoomsday ...
jumlah    : 2

foto 1       : https://dl.tiktokio.com/download?token=...
foto 2       : https://dl.tiktokio.com/download?token=...
musik        : https://dl.tiktokio.com/download?token=...
```

Isi bloknya seadanya — yang ada diisi, yang tidak ada tidak ditampilkan:

- **type** — `video` atau `photo`
- **pengupload** — username akunnya (diambil dari link; nama tampilan tidak tersedia)
- **caption** — teks postingan (bisa kosong kalau postingannya memang tanpa caption)
- **jumlah** — khusus postingan foto: banyaknya foto
- **video** — satu link, kualitas terbaik tanpa watermark
- **foto 1, foto 2, ...** — khusus postingan foto
- **musik** — audio postingan sebagai MP3 (kalau ada)
- **cover** — gambar sampul (kalau ada)

Link download-nya bertanda tangan token dan **kedaluwarsa setelah beberapa jam** — jalankan lagi script-nya untuk dapat link yang segar.

### 2. Unduh langsung ke disk (opsional)

```bash
python3 tiktok.py download "<link>" [folder-tujuan]
```

- Postingan video → file kualitas terbaik tanpa watermark-nya, nama `<id>_<username>.mp4`
- Postingan foto → semua gambarnya ke subfolder `<id>_<username>/` (`01.jpg`, `02.jpg`, dst)
- Tanpa `[folder-tujuan]`, file disimpan di folder saat ini

### Format link yang didukung

- Link penuh: `https://www.tiktok.com/@user/video/<id>` dan `https://www.tiktok.com/@user/photo/<id>`
- Link pendek hasil share: `https://vt.tiktok.com/...` dan `https://vm.tiktok.com/...`

Hanya postingan publik yang bisa diproses.

---

## Catatan

Tool ini bekerja dengan memakai layanan **tiktokio** (situs tiktokio.com): link dikirim ke API internal situs tersebut — endpoint yang sama dengan yang dipakai halaman webnya — lalu link download diambil dari jawabannya, dan file-nya disajikan dari server mereka (`*.tiktokio.com`). Konsekuensinya: kualitas videonya sampai kualitas orisinal yang tidak ditawarkan halaman web TikTok, tapi tool ini **bergantung pada pihak ketiga** — kalau tiktokio mati atau menutup aksesnya, tool ini ikut mati.
