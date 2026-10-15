"""Rekomendasi Film - pilihan nonton pribadi.

Bedanya sama project kuliner: di sini kamu ketik kata (hantu, lucu, perang),
programnya nyaranin genre mana yang paling nyambung, terus ngasih daftar film
di genre itu. Semua data disimpan di data_film.json, jadi bisa ditambah,
ratingnya diubah, atau dihapus langsung dari program.

Algoritma yang dipakai (sesuai brief project):
    - pencarian biner  : cari_judul_biner()
    - pencarian linier : cari_kata_kunci()
    - pengurutan       : urutkan() (rating / tahun / durasi / judul)
    - skoring          : saran_kategori() buat menebak genre

Fitur:
    1. Cari dari kata kunci (dapat saran genre + rekomendasi)
    2. Cari judul
    3. Paket marathon (total durasi nggak lebih dari batas)
    4. Kelola data (tambah / ubah rating / hapus)
    5. Lihat semua data (bisa pilih urutan)
    6. Keluar

Cara jalan: python film.py
"""

from itertools import combinations
import json
import math
import os

NAMA_FILE = "data_film.json"
GENRE_VALID = ["aksi", "drama", "komedi", "horor", "animasi", "dokumenter"]
URUTAN_VALID = ["rating", "tahun", "durasi", "judul"]

# Kamus kecil: kata yang biasa diketik orang -> genre.
# Ini pelengkap, bukan satu-satunya sumber: judul film di data juga ikut dinilai.
PETA_KATA = {
    "aksi": [
        "tembak",
        "perang",
        "kejar",
        "jahat",
        "detektif",
        "pahlawan",
        "superhero",
        "senjata",
        "kejahatan",
        "ledakan",
        "kejar-kejaran",
        "pertarungan",
        "spionase",
    ],
    "drama": [
        "sedih",
        "haru",
        "keluarga",
        "kehidupan",
        "perjuangan",
        "persahabatan",
        "harapan",
        "emosi",
        "mengharukan",
        "serius",
    ],
    "komedi": [
        "lucu",
        "konyol",
        "hiburan",
        "ketawa",
        "jenaka",
        "lawak",
        "santai",
        "bercanda",
        "ngakak",
    ],
    "horor": [
        "hantu",
        "seram",
        "menakutkan",
        "ketakutan",
        "zombie",
        "teror",
        "mencekam",
        "setan",
        "angker",
        "gelap",
    ],
    "animasi": [
        "kartun",
        "animasi",
        "anak",
        "dongeng",
        "imajinasi",
        "lucu",
        "petualangan",
    ],
    "dokumenter": [
        "fakta",
        "nyata",
        "sejarah",
        "riwayat",
        "alam",
        "satwa",
        "dokumenter",
        "pendidikan",
    ],
}


# ---------------------------------------------------------------------------
# Bagian data (baca / tulis file)
# ---------------------------------------------------------------------------


def muat_data(path=NAMA_FILE):
    """Baca data dari file JSON. Kalau file belum ada, balikin list kosong."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def simpan_data(data, path=NAMA_FILE):
    """Tulis data ke file JSON."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


# ---------------------------------------------------------------------------
# Bagian logika (murni, nggak nyentuh file - gampang dites)
# ---------------------------------------------------------------------------


def parse_angka(teks):
    """Ubah input jadi bilangan bulat positif. Salah atau nol -> None."""
    bersih = teks.replace(".", "").replace(",", "").replace(" ", "").strip()
    if not bersih.lstrip("-").isdigit():
        return None
    nilai = int(bersih)
    return nilai if nilai > 0 else None


def parse_rating(teks):
    """Ubah input jadi rating 0-10 (boleh desimal). Salah -> None."""
    bersih = teks.replace(",", ".").replace(" ", "").strip()
    try:
        nilai = float(bersih)
    except ValueError:
        return None
    if 0 <= nilai <= 10:
        return round(nilai, 1)
    return None


def format_durasi(menit):
    """Ubah 152 jadi '2 j 32 m'. Buat nampilin total marathon."""
    jam, sisa = divmod(int(menit), 60)
    if jam and sisa:
        return f"{jam} j {sisa} m"
    if jam:
        return f"{jam} j"
    return f"{sisa} m"


def bulatkan_nilai(nilai):
    """Bulatkan ke 1 desimal, setengahnya dibulatkan ke atas.

    Python bawaan pakai round-half-even: round(8.25, 1) -> 8.2.
    JavaScript di versi web pakai half-up: (8.25).toFixed(1) -> "8.3".
    Biar CLI dan web nunjukkin angka yang sama, di sini dipaksa half-up.
    """
    return math.floor(nilai * 10 + 0.5) / 10


def skor_genre(data, kata, genre):
    """Seberapa nyambung kata user sama satu genre. Angka >= 0."""
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


def saran_kategori(data, kata):
    """Balikin daftar (genre, skor) dari yang paling nyambung ke yang paling
    nggak. Genre dengan skor 0 dibuang, jadi hasil kosong = nggak ada saran."""
    bertahan = []
    for genre in GENRE_VALID:
        skor = skor_genre(data, kata, genre)
        if skor > 0:
            bertahan.append((genre, skor))

    # Skor tertinggi dulu; kalau seri, urutan bawaan GENRE_VALID yang menang.
    bertahan.sort(key=lambda pasangan: (-pasangan[1], GENRE_VALID.index(pasangan[0])))
    return bertahan


def cari_film(data, genre=None):
    """Ambil film satu genre. genre=None artinya ambil semua."""
    if genre is None:
        return list(data)
    return [film for film in data if film["genre"] == genre]


def urutkan(data, kunci="rating", menaik=False):
    """Urutkan daftar film.

    rating : tertinggi dulu
    tahun  : terbaru dulu
    durasi : paling pendek dulu
    judul  : abjad A-Z
    """
    if kunci not in URUTAN_VALID:
        raise ValueError(f"Urutan '{kunci}' nggak dikenal. Pilih {URUTAN_VALID}.")

    if kunci == "judul":
        return sorted(data, key=lambda film: film["judul"].lower(), reverse=menaik)
    if kunci == "tahun":
        return sorted(data, key=lambda film: film["tahun"], reverse=not menaik)
    if kunci == "durasi":
        return sorted(data, key=lambda film: film["durasi"], reverse=menaik)
    return sorted(data, key=lambda film: film["rating"], reverse=not menaik)


def cari_judul_biner(data, judul):
    """Cari film berdasarkan awal judul pakai pencarian biner.

    Daftar disorting dulu abjad, terus dipotong dua berkali sampai ketemu
    titik masuknya, baru dari situ ditelusuri ke kanan selama masih sama
    awalan. Hasilnya list (bisa kosong).
    """
    target = judul.lower().strip()
    if not target:
        return []

    antrian = sorted(data, key=lambda film: film["judul"].lower())

    # Cari index pertama yang judulnya >= target (lower bound).
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
    return hasil


def cari_kata_kunci(data, kata):
    """Pencarian linier: cocokkan kata di judul, tahun, atau catatan."""
    kata = kata.lower().strip()
    if not kata:
        return []
    return [
        film
        for film in data
        if kata in film["judul"].lower()
        or kata in str(film["tahun"])
        or kata in film.get("catatan", "").lower()
    ]


def rekomendasi_serupa(data, film, jumlah=3):
    """Film segenre dengan rating paling dekat, dan utamakan yang sezaman."""
    kandidat = [
        lain
        for lain in data
        if lain["genre"] == film["genre"] and lain["judul"] != film["judul"]
    ]
    kandidat.sort(key=lambda lain: abs(lain["rating"] - film["rating"]))

    sezaman = [lain for lain in kandidat if abs(lain["tahun"] - film["tahun"]) <= 10]
    beda_zaman = [lain for lain in kandidat if abs(lain["tahun"] - film["tahun"]) > 10]
    return (sezaman + beda_zaman)[:jumlah]


def _kombinasi_terbaik(data, batas_menit, jumlah):
    """Kombinasi `jumlah` film dengan total durasi paling mendekati batas.

    Dua langkah pembanding: total durasi dulu (makin mentok makin bagus),
    kalau seri baru rating totalnya yang menang.
    """
    terbaik = None
    for isi in combinations(data, jumlah):
        total = sum(film["durasi"] for film in isi)
        if total > batas_menit:
            continue
        skor = (total, sum(film["rating"] for film in isi))
        if terbaik is None or skor > terbaik["skor"]:
            terbaik = {
                "film": list(isi),
                "total": total,
                "rating_rata": bulatkan_nilai(skor[1] / jumlah),
                "sisa": batas_menit - total,
                "skor": skor,
            }
    return terbaik


def paket_marathon(data, batas_menit, jumlah_maks=3):
    """Rakit paket nonton yang total durasinya nggak lewat batas.

    Mulai dari film paling banyak, mundur sampai 1. Kalau sama sekali nggak
    muat (durasi tunggal aja udah lewat), balikin None.
    """
    if not data:
        return None
    for jumlah in range(jumlah_maks, 0, -1):
        hasil = _kombinasi_terbaik(data, batas_menit, jumlah)
        if hasil:
            return hasil
    return None


# ---------------------------------------------------------------------------
# Bagian tampilan
# ---------------------------------------------------------------------------


def tanya(prompt):
    """input() yang nggak bikin program error kalau sesi dihentikan."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nOke, sampai jumpa.")
        raise SystemExit(0)


def tampilkan_daftar(daftar, batas_menit=None):
    if not daftar:
        print("\nNggak ada yang cocok. Coba kata, genre, atau batasnya diganti.")
        return

    print()
    for nomor, film in enumerate(daftar, start=1):
        baris = (
            f"{nomor}. {film['judul']:<36} {film['tahun']}"
            f"  {film['durasi']:>3} mnt  {film['rating']:>4.1f}"
        )
        if batas_menit:
            sisa = batas_menit - film["durasi"]
            baris += f"  sisa {format_durasi(sisa)}"
            if film["durasi"] <= batas_menit * 0.5:
                baris += "  (ringan)"
        catatan = film.get("catatan", "")
        if catatan:
            baris += f"  [{catatan}]"
        print("  " + baris)
    print()


def tampilkan_saran(kata, saran):
    print(f"\nSaran genre buat '{kata}':")
    for genre, skor in saran:
        print(f"   - {genre:<12} skor {skor}")


def tampilkan_rekomendasi_serupa(data, film):
    print(f"\nKamu pilih {film['judul']} ({film['tahun']}). Yang mirip:")
    for lain in rekomendasi_serupa(data, film):
        print(
            f"   - {lain['judul']:<36} {lain['tahun']}"
            f"  {lain['durasi']:>3} mnt  {lain['rating']:>4.1f}"
        )
    print()


def tampilkan_paket(paket, batas_menit):
    if paket is None:
        print(f"\nBatas {format_durasi(batas_menit)} nggak cukup buat nonton apa pun.")
        print("Coba naikkan batasnya, ya.")
        return

    print(f"\nPaket marathon batas {format_durasi(batas_menit)}:")
    print()
    for film in paket["film"]:
        print(f"   - {film['judul']:<36} {film['durasi']:>3} mnt")
    print()
    print(f"  Total   : {format_durasi(paket['total'])}")
    print(f"  Rating  : rata-rata {paket['rating_rata']}")
    print(f"  Sisa    : {format_durasi(paket['sisa'])}")
    print()


# ---------------------------------------------------------------------------
# Bagian input
# ---------------------------------------------------------------------------


def tanya_angka(prompt, jumlah):
    """Minta nomor urut 1..jumlah. Balikin index (0-based) atau None."""
    jawab = tanya(prompt).strip()
    if jawab.isdigit() and 1 <= int(jawab) <= jumlah:
        return int(jawab) - 1
    return None


def tanya_genre():
    while True:
        teks = tanya("  Genre (aksi / drama / komedi / horor / animasi / dokumenter): ")
        teks = teks.strip().lower()
        if teks in GENRE_VALID:
            return teks
        print("  Genre-nya nggak ada di daftar. Coba ketik salah satu dari tadi.\n")


def tanya_durasi():
    while True:
        teks = tanya("  Durasi dalam menit (contoh 120): ")
        durasi = parse_angka(teks)
        if durasi is None:
            print("  Isinya harus angka lebih dari 0, ya.\n")
            continue
        return durasi


def tanya_rating():
    while True:
        teks = tanya("  Rating 0-10 (contoh 8.5): ")
        rating = parse_rating(teks)
        if rating is None:
            print("  Rating harus angka 0 sampai 10.\n")
            continue
        return rating


def pilih_genre_dari_saran(saran):
    """Minta user pilih genre. Kosong = ambil saran pertama."""
    while True:
        teks = tanya("  Lihat rekomendasi genre mana? (Enter = ambil saran teratas): ")
        teks = teks.strip().lower()
        if not teks:
            return saran[0][0]
        if teks in [genre for genre, _ in saran]:
            return teks
        if teks in GENRE_VALID:
            return teks
        print("  Nggak ada di saran tadi. Ketik salah satu genre di atas.\n")


# ---------------------------------------------------------------------------
# Bagian kelola data
# ---------------------------------------------------------------------------


def tambah_data(data):
    print("\nCatat film baru.")
    judul = tanya("  Judul film: ").strip()
    if not judul:
        print("  Judul nggak boleh kosong.")
        return

    duplikat = [film for film in data if film["judul"].lower() == judul.lower()]
    if duplikat:
        print(f"  '{judul}' udah ada di data. Batal nambah.")
        return

    genre = tanya_genre()

    while True:
        tahun = parse_angka(tanya("  Tahun rilis (contoh 2019): "))
        if tahun:
            if 1888 <= tahun <= 2100:
                break
            print("  Tahunnya kelihatan nggak wajar (1888-2100).\n")
        else:
            print("  Tahun harus angka.\n")

    durasi = tanya_durasi()
    rating = tanya_rating()
    catatan = tanya("  Catatan (boleh kosong): ").strip()

    data.append(
        {
            "judul": judul,
            "genre": genre,
            "tahun": tahun,
            "durasi": durasi,
            "rating": rating,
            "catatan": catatan,
        }
    )
    simpan_data(data)
    print(f"\n  Tersimpan: {judul} ({genre}, {rating}).")


def ubah_rating(data):
    if not data:
        print("\n  Belum ada data.")
        return
    tampilkan_daftar(urutkan(data, "judul"))
    pilih = tanya_angka("  Nomor yang mau diubah ratingnya: ", len(data))
    if pilih is None:
        print("  Nomornya nggak ada.")
        return
    film = urutkan(data, "judul")[pilih]
    print(f"  {film['judul']} sekarang rating {film['rating']}.")
    rating = tanya_rating()
    lama = film["rating"]
    film["rating"] = rating
    simpan_data(data)
    print(f"\n  Rating {film['judul']}: {lama} -> {rating}.")


def hapus_data(data):
    if not data:
        print("\n  Belum ada data.")
        return
    urut = urutkan(data, "judul")
    tampilkan_daftar(urut)
    pilih = tanya_angka("  Nomor yang mau dihapus: ", len(urut))
    if pilih is None:
        print("  Nomornya nggak ada.")
        return
    film = urut[pilih]
    konfirmasi = tanya(f"  Hapus '{film['judul']}'? (y/n): ").strip().lower()
    if konfirmasi == "y":
        data.remove(film)
        simpan_data(data)
        print(f"\n  '{film['judul']}' udah dihapus.")
    else:
        print("\n  Batal, nggak jadi dihapus.")


def kelola_data(data):
    while True:
        print("\nKelola data saya:")
        print("  1. Tambah film baru")
        print("  2. Ubah rating")
        print("  3. Hapus data")
        print("  4. Kembali")
        pilih = tanya("  Pilih (1/2/3/4): ").strip()

        if pilih == "1":
            tambah_data(data)
        elif pilih == "2":
            ubah_rating(data)
        elif pilih == "3":
            hapus_data(data)
        elif pilih == "4":
            return
        else:
            print("  Nggak ada menu itu. Ketik 1, 2, 3, atau 4.")


def tanya_urutan():
    print("\n  Urutkan berdasar:")
    print("    1. Rating (tertinggi dulu)")
    print("    2. Tahun (terbaru dulu)")
    print("    3. Durasi (paling pendek dulu)")
    print("    4. Judul (abjad)")
    peta = {"1": "rating", "2": "tahun", "3": "durasi", "4": "judul"}
    while True:
        pilih = tanya("  Pilih (1/2/3/4): ").strip()
        if pilih in peta:
            return peta[pilih]
        print("  Nggak ada pilihan itu.\n")


def lihat_semua(data):
    if not data:
        print("\n  Belum ada data. Pakai menu 4 buat nambah.")
        return
    kunci = tanya_urutan()
    urut = urutkan(data, kunci)

    print(f"\nSEMUA FILM ({len(urut)}) - urut {kunci}:")
    print(f"  {'-' * 72}")
    for film in urut:
        baris = (
            f"  {film['judul']:<36} {film['genre']:<11} {film['tahun']}"
            f"  {film['durasi']:>3} mnt  {film['rating']:>4.1f}"
        )
        if film.get("catatan"):
            baris += f"  [{film['catatan']}]"
        print(baris)
    print()


def ringkasan(data):
    print("\nRingkasan per genre:")
    for genre in GENRE_VALID:
        isi = cari_film(data, genre)
        if not isi:
            continue
        rata = bulatkan_nilai(sum(film["rating"] for film in isi) / len(isi))
        print(f"  {genre:<11} {len(isi):>2} film  rating rata-rata {rata:.1f}")
    print()


# ---------------------------------------------------------------------------
# Program utama
# ---------------------------------------------------------------------------


def main():
    data = muat_data()

    print("=" * 58)
    print("  REKOMENDASI FILM SAYA")
    print(f"  {len(data)} film tercatat")
    print("=" * 58)

    if not data:
        print("\nData masih kosong. File data_film.json belum ada isinya.")

    while True:
        print("\nMau ngapain?")
        print("  1. Cari dari kata kunci (dapat saran genre)")
        print("  2. Cari judul")
        print("  3. Paket marathon (batas total durasi)")
        print("  4. Kelola data saya")
        print("  5. Lihat semua data")
        print("  6. Keluar")
        pilihan = tanya("  Pilih (1-6): ").strip()

        if pilihan == "1":
            kata = tanya("  Ketik kata (mis. hantu, lucu, perang): ").strip()
            if not kata:
                print("  Kata kuncinya kosong, ya.")
                continue
            saran = saran_kategori(data, kata)
            if not saran:
                print(f"\nNggak ada genre yang nyambung sama '{kata}'.")
                print("Coba kata lain: hantu, lucu, sedih, kartun, fakta, perang.")
                continue

            tampilkan_saran(kata, saran)
            genre = pilih_genre_dari_saran(saran)
            hasil = urutkan(cari_film(data, genre), "rating")
            print(f"\nRekomendasi {genre} (rating tertinggi dulu):")
            tampilkan_daftar(hasil)

            if hasil:
                pilih = tanya_angka(
                    "  Mau lihat yang mirip? Ketik nomornya, atau Enter buat lanjut: ",
                    len(hasil),
                )
                if pilih is not None:
                    tampilkan_rekomendasi_serupa(data, hasil[pilih])

        elif pilihan == "2":
            judul = tanya("  Ketik awal judul film: ").strip()
            hasil = cari_judul_biner(data, judul)
            if hasil:
                print(f"\nHasil pencarian biner '{judul}':")
                tampilkan_daftar(hasil)
            else:
                # Pencarian biner cuma bisa nangkep awal judul, jadi fallback.
                cadangan = cari_kata_kunci(data, judul)
                print(f"\nPencarian biner '{judul}' nggak ketemu.")
                if cadangan:
                    print("Pakai pencarian linier (cocok di mana aja):")
                    tampilkan_daftar(cadangan)
                else:
                    print("Pencarian linier juga nggak ketemu apa-apa.")

        elif pilihan == "3":
            while True:
                teks = tanya("  Batas total durasi dalam menit (contoh 240): ")
                batas = parse_angka(teks)
                if batas:
                    break
                print("  Isinya harus angka lebih dari 0, ya.\n")
            tampilkan_paket(paket_marathon(data, batas), batas)

        elif pilihan == "4":
            kelola_data(data)

        elif pilihan == "5":
            lihat_semua(data)
            if data:
                ringkasan(data)

        elif pilihan == "6":
            print("\nSip, makasih. Selamat nonton!\n")
            break

        else:
            print("  Nggak ada menu itu. Ketik angka 1 sampai 6.")


if __name__ == "__main__":
    main()
