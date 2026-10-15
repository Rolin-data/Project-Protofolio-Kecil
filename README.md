# Rekomendasi Film

Program rekomendasi film versi terminal. Kamu ketik kata apa aja (`hantu`,
`lucu`, `perang`), programnya nyaranin **genre mana yang paling nyambung**,
terus ngasih daftar film di genre itu beserta yang mirip-miripnya.

Project ini jawaban buat Codecademy
[Recommendation Software](https://www.codecademy.com/projects/portfolio/recommendation-software-project),
topik **Movies**. Sengaja nggak berhenti di kodingan mentah: datanya ditaruh di
file JSON terpisah, logikanya diuji unit test, terus dibikinin versi web + tulisan
teknisnya.

## Fitur

1. **Cari dari kata kunci** — ketik `hantu`, keluar saran `horor`, lalu daftar
   film horor dari rating tertinggi. Kalau nggak nyambung, program bilang jujur
   dan ngasih contoh kata yang bisa dicoba.
2. **Cari judul** — pencarian biner di daftar yang udah diurutkan abjad. Kalau
   nggak ketemu, otomatis fallback ke pencarian linier.
3. **Paket marathon** — kasih batas total durasi (mis. 240 menit), program nyusun
   kombinasi film yang paling mentok ke batas itu.
4. **Kelola data** — tambah film, ubah rating, hapus. Langsung nulis ke JSON.
5. **Lihat semua data** — bisa dipilih urutannya: rating, tahun, durasi, atau
   judul. Ditambah ringkasan jumlah film + rating rata-rata per genre.

## Data

Sumber tunggalnya `data_film.json`, dipakai bareng oleh versi CLI dan versi web
jadi nggak ada data yang diduplikasi.

```json
{
  "judul": "The Dark Knight",
  "genre": "aksi",
  "tahun": 2008,
  "durasi": 152,
  "rating": 9.0,
  "catatan": ""
}
```

- **36 film**, 6 genre × 6 film: `aksi`, `drama`, `komedi`, `horor`, `animasi`,
  `dokumenter`.
- `rating` adalah **penilaian pribadi skala 0–10, bukan IMDb**. Bebas kamu ubah
  lewat menu kelola data.
- `durasi` masih perkiraan, satuan menit.
- `catatan` sengaja dikosongin buat diisi kamu (mis. *"buat malam Jumat"*).

## Algoritma

Sesuai brief project: nyimpan data di struktur data, lalu pakai algoritma
sort/search di atasnya.

| Fungsi | Algoritma |
|--------|-----------|
| `saran_kategori()` | Skoring bertingkat — nama genre (+5), cocok di kamus kata kunci (+4/+3/+1), judul film yang mengandung kata (+2), lalu diurutkan turun |
| `cari_judul_biner()` | **Binary search** buat cari lower bound awal judul, lalu ditelusuri ke kanan selama awalannya sama |
| `cari_kata_kunci()` | **Linear search** — cocokin kata di judul, tahun, dan catatan |
| `urutkan()` | Sorting by rating / tahun / durasi / judul |
| `paket_marathon()` | Kombinasi semua kemungkinan film (max 3), ambil yang total durasinya paling mendekati batas; kalau seri, rating total yang menang. Mundur ke 2 lalu 1 film kalau nggak muat |
| `rekomendasi_serupa()` | Segenre → selisih rating terkecil → utamakan yang sezaman (beda ≤ 10 tahun) |

Kamus kata kunci (`PETA_KATA`) cuma pelengkap. Sumber skor utamanya tetap
data di JSON, jadi begitu kamu nambah film dengan judul baru, tebakannya ikut
membaik sendiri.

## Versi web

`index.html` — HTML + Tailwind (CDN) + JavaScript polos, tanpa backend. Halaman
dibikin seperti katalog film pada umumnya: header lengket berisi navigasi dan
kolom pencarian, kartu "Jelajahi genre", daftar film dalam bentuk tabel (nomor,
judul, tahun, durasi, rating), filter genre, pilihan urutan, paket marathon, dan
detail "film mirip" yang bisa dibuka per baris.

Logika JS-nya ditulis ulang dari `film.py` supaya hasilnya sama: skoring genre,
pengurutan, dan kombinasi marathon. Satu beda kecil — pencarian di web memakai
filter linier karena seluruh data sudah ada di memori, sedangkan pencarian biner
tetap dipakai di versi CLI.

Versi web **read-only**: ngedit data tetap lewat CLI atau langsung edit
`data_film.json`.

Karena browser nggak boleh ambil file lain lewat `file://`, jalankan lewat server
lokal:

```powershell
python -m http.server 8000
# buka http://localhost:8000
```

## Pengujian

```powershell
python -m unittest -v test_film
```

65 unit test `unittest`, semuanya ngecek logika murni (parsing input, skoring
genre, binary search, sorting, kombinasi marathon). Satu kelas khusus baca
`data_film.json` beneran buat mastiin datanya sehat: jumlah, kelengkapan field,
genre valid, judul unik, dan rentang nilai.

Uji jalan CLI (tanpa ngerusak data asli):

```powershell
cmd /c "python film.py < test_input.txt"
```

Catatan: `test_input.txt` memuat menu kelola data, jadi kalau dijalankan langsung
di folder ini, `data_film.json` bakal berubah. Untuk coba-coba, salin dulu ke
folder lain.

## Menjalankan

```powershell
python film.py
```

## Struktur folder

```
Rekomendasi-Film/
├── film.py            # program CLI
├── data_film.json     # data (sumber tunggal)
├── index.html         # versi web
├── test_film.py       # unit test
├── test_input.txt     # input uji CLI
├── BLOG_POST.md       # tulisan teknis (sumber)
├── BLOG_POST.html     # tulisan teknis (versi web)
├── convert_blog.py    # generator BLOG_POST.html
└── README.md
```

## Link

- **Demo web:** https://rolin-data.github.io/Rekomendasi-Film/
- **Tulisan teknis:** https://rolin-data.github.io/Rekomendasi-Film/BLOG_POST.html
- **Repo:** https://github.com/Rolin-data/Rekomendasi-Film
