# Dari Kata "Hantu" Sampai Daftar Film: Bikin Program Rekomendasi

Program rekomendasi itu kelihatan gampang kalau baru dilihat sekilas: user ketik
sesuatu, program kasih saran. Masalahnya, "sesuatu" itu nggak pernah rapi. Orang
ngetik `hantu`, ada yang ngetik `seram`, ada juga yang cuma ngetik `hur` karena
keburu Enter. Tulisan ini bongkar gimana program rekomendasi film ini bekerja di
dalamnya, dan tiga hal kecil yang nyaris bikin salah kaprah.

## Masalahnya bukan di kodenya, tapi di datanya

Brief project-nya minta lima hal: simpan data di struktur data, pakai algoritma
sort/search, pakai Git, pakai command line, dan tulis blog teknis. Bagian
"struktur data" adalah yang paling gampang disepelekan.

Versi pertamanya sempat lewat di kepala: taruh daftar film sebagai list of dict
langsung di dalam file Python. Tapi begitu ada yang mau nambah film, dia harus
buka file `.py`. Alhasil datanya dipindah ke file sendiri:

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

Sekarang `data_film.json` jadi satu-satunya sumber. Program terminal baca file
itu, halaman web juga fetch file yang sama. Nggak ada data yang diduplikasi, jadi
nggak mungkin ada dua versi yang beda.

Isinya 36 film, enam genre masing-masing enam film. `rating` sengaja ditulis
sebagai penilaian pribadi 0–10, bukan angka IMDb — biar nggak ada klaim angka
yang belum tentu benar. `catatan` sengaja kosong, itu memang buat diisi user.

## Bagian inti: menebak genre dari kata acak

Di sinilah bagian paling menarik. Program nggak punya kamus sinonim yang rapi,
dan jujur aja, bikin kamus kayak gitu buat 6 genre terasa berlebihan.

Yang dipakai adalah **skoring bertingkat**. Tiap genre dinilai dari tiga sinyal:

```python
def skor_genre(data, kata, genre):
    kata = kata.lower().strip()
    if not kata:
        return 0

    skor = 0

    # 1. Nama genrenya sendiri ketik langsung, mis. "hor" masuk di "horor".
    if kata in genre or genre in kata:
        skor += 5

    # 2. Ada di kamus kata kunci genre ini.
    for kunci in PETA_KATA.get(genre, []):
        if kata == kunci:
            skor += 4
        elif kata in kunci:
            skor += 3
        elif kunci in kata:
            skor += 1

    # 3. Judul film di genre ini mengandung kata tersebut.
    for film in data:
        if film["genre"] == genre and kata in film["judul"].lower():
            skor += 2

    return skor
```

Yang bikin penasaran: kenapa nggak cuma poin 2 aja? Soalnya poin 2 itu mati.
Kamus kata kunci itu isinya kata-kata yang sudah aku tulis sendiri, jadi dia
cuma sebagus daftar tadi. Poin 3 bikin sistemnya **ikut belajar dari data**.
Begitu kamu nambah film berjudul *Night of the Living Dead* ke genre horor, kata
`night` otomatis dapet tambahan skor tanpa ada yang menyentuh kode.

Poin 1 kelihatannya aneh sampai dicoba dengan input huruf doang. Ketik `a`, dan
`"a" in "aksi"` itu benar, jadi `aksi` langsung dapat 5. Ini yang bikin brief
nyebut "entering **letters** or words" — huruf tunggal pun tetap nghasilin
saran, bukan error.

Setelah skor dikumpulin, tinggal:

```python
def saran_kategori(data, kata):
    bertahan = []
    for genre in GENRE_VALID:
        skor = skor_genre(data, kata, genre)
        if skor > 0:
            bertahan.append((genre, skor))

    bertahan.sort(key=lambda pasangan: (-pasangan[1], GENRE_VALID.index(pasangan[0])))
    return bertahan
```

Genre dengan skor 0 dibuang. Ini penting: `saran_kategori(data, "zzzq")` harus
balikin list kosong, dan program harus **berani bilang nggak tahu** alih-alih
mendem ke genre pertama.

## Pencarian biner yang berguna

Bagian binary search di kebanyakan tutorial berhenti di "ketemu nggak ketemu".
Itu terlalu kaku buat pemakaian beneran — orang ngetik `the`, dan ada tujuh film
yang judulnya diawali `the`.

Jadi dipakai dua langkah: **lower bound** dulu buat nyari index pertama yang
judulnya lebih besar atau sama, baru ditelusuri ke kanan selama awalannya masih
sama.

```python
    kiri, kanan = 0, len(antrian)
    while kiri < kanan:
        tengah = (kiri + kanan) // 2
        if antrian[tengah]["judul"].lower() < target:
            kiri = tengah + 1
        else:
            kanan = tengah

    hasil = []
    while kiri < len(antrian) and antrian[kiri]["judul"].lower().startswith(target):
        hasil.append(antrian[kiri])
        kiri += 1
```

Kompleksitasnya tetap `O(log n)` buat bagian cari. Keterbatasannya jujur
disebut: binary search cuma bisa nangkep **awal** judul. Ketik `shawshank`
(bukan `the shawshank`) dia bakal gagal. Makanya ada fallback pencarian linier
di menu yang sama, dan programnya menulis jujur di layar kalau yang dipakai
adalah pencarian linier.

## Marathon: kombinasi yang paling mentok

Menu ketiga nyusun paket nonton dari batas total durasi. Sederhananya ini
pekerjaan kombinatorik kecil: semua kemungkinan 3 film dari 36 itu
`C(36,3) = 7.140` kombinasi. Masih gampang ditelusuri satu-satu, nggak perlu
dynamic programming yang bikin kodenya susah dibaca.

Yang perlu hati-hati adalah **pembandingnya**. Kalau cuma `total > terbaik`, film
dengan total 240 menit tapi rating 6.0 bisa menang lawan total 240 menit rating
9.5 yang urutannya kalah duluan. Maka dipakai tuple:

```python
        skor = (total, sum(film["rating"] for film in isi))
        if terbaik is None or skor > terbaik["skor"]:
```

Karena tuple di Python dibandingkan elemen per elemen, durasi tetap yang utama
sesuai brief (mentok ke batas), rating cuma jadi pembeda waktu seri. Kalau sama
sekali nggak muat, program mundur ke 2 film, lalu 1 film.

## Dua bahasa, satu hasil — dan masalah 0,1

Versi web ditulis JavaScript, versi terminal ditulis Python. Logikanya sengaja
ditulis paralel biar hasilnya sama. Eh, ternyata nggak sama.

Rata-rata rating 6 film aksi keluar **8.25**. Di Python:

```python
>>> f"{8.25:.1f}"
'8.2'
```

Di JavaScript:

```js
(8.25).toFixed(1)  // "8.3"
```

Python memakai *round-half-even* (setengah dibulatkan ke bilangan genap), JS
memakai *half-up*. Nol koma doang, tapi CLI nunjukin 8.2 dan web nunjukin 8.3
untuk data yang identik — dan itu jelas kelihatan begitu dua jendelanya
dibuka berdua.

Solusinya bukan memaksa salah satunya pindah cara, tapi menyamakan aturannya di
satu tempat:

```python
def bulatkan_nilai(nilai):
    """Bulatkan ke 1 desimal, setengahnya dibulatkan ke atas."""
    return math.floor(nilai * 10 + 0.5) / 10
```

Hal kecil, tapi ini persis jenis bug yang bikin orang nggak percaya program
rekomendasi: angkanya beda-beda tiap dibuka.

## Bug yang ketangkep pas ngoding

Dua yang paling diingat:

**Chip genre numpuk.** Di halaman web, klik kata kunci → muncul chip genre →
klik salah satu chip. Waktu pertama ditulis, handler-nya nambah blok rekomendasi
pakai `innerHTML +=`. Klik chip kedua, bloknya nambah lagi, bukan ganti. Kelihatan
pas dihitung jumlah anaknya: harusnya tetap 2, kejadian jadi 3, 4, 5. Diperbaiki
dipisahnya jadi dua wadah: wadah chip dirender sekali, wadah rekomendasi yang
diganti.

**Input uji yang salah sendiri.** Programnya jalan bener, cuma file input ujinya
kurang satu baris kosong, jadi jawaban Enter-nya keseleweng ke prompt berikutnya
dan menu 2 nggak pernah kejalan. Gampang ngira-ngira itu bug program. Dicek
lagi satu-satu, ternyata inputnya.

## Ngetes yang nggak kelihatan

65 unit test dipisah jadi dua kubu: logika murni yang nggak nyentuh file (jadi
nggak mungkin ngerusak data), dan satu kelas khusus yang baca
`data_film.json` beneran buat mastiin datanya sehat — jumlahnya, kelengkapan
field, genre valid, judul unik, rentang tahun dan rating.

Yang paling bikin lega justru test skoring genre: `saran_kategori(DATA, "hantu")`
harus nyalonin `horor` duluan. Kalau suatu hari ada yang iseng ngubah `PETA_KATA`
dan bikin `aksi` menang, test-nya langsung teriak.

Uji jalan buat menu kelola data dijalankan di salinan folder, bukan folder
aslinya. Soalnya menu itu emang nulis file — dan memang sempat kejadian datanya
berubah duluan sebelum keingat. Untung ada test yang langsung ngomong jumlahnya
bukan 36 lagi.

## Versi web tanpa backend

`index.html` itu HTML + Tailwind dari CDN + JavaScript polos. Nggak ada server
API, nggak ada framework. Cuma `fetch("data_film.json")`, terus logika yang sama
ditulis ulang dalam JavaScript.

Tampilannya sengaja dibikin seperti katalog film pada umumnya — header lengket,
kolom pencarian, tabel berisi nomor/judul/tahun/durasi/rating — biar nggak terasa
seperti halaman contoh. Satu beda kecil: pencarian di web memakai filter linier di
sisi klien karena datanya sudah ada di memori, sedangkan pencarian biner tetap
dipakai di versi terminal.

Konsekuensinya versi web itu **read-only**. Mau nambah film ya lewat terminal atau
langsung edit JSON-nya. Buat project seukuran ini itu justru masuk akal: nambah
endpoint CRUD berarti nambah server, nambah deploy, dan nambah tempat buat bug.

## Yang dipelajari

1. Pisahin data dari kode dari awal. Semua yang menyusahkan setelah itu biasanya
   berawal dari keputusan nyimpen data di tempat yang salah.
2. Sistem rekomendasi yang jujur itu yang berani bilang *"nggak ada yang cocok"*.
3. Konsistensi hasil antar implementasi itu detail yang gampang dilewatin dan
   gampang kelihatan.
4. Test yang baca data beneran itu bukan test logika, tapi test dokumentasi —
   dan dia yang paling sering nyelametin.

## Link

- [Demo web](https://rolin-data.github.io/Project-Protofolio-Kecil/)
- [Repo GitHub](https://github.com/Rolin-data/Project-Protofolio-Kecil)
- [Baca juga: project kuliner sebelumnya](https://rolin-data.github.io/Rekomendasi-Kuliner-Di-Indonesia/BLOG_POST.html)
