"""Unit test buat logika di film.py.

Jalanin dengan:  python -m unittest -v

Test logika nggak nyentuh data_film.json, jadi hasilnya selalu sama.
Cuma TestDataFile yang baca file beneran buat mastiin datanya sehat.
"""

import os
import unittest

import film

# Data buatan khusus buat tes. Durasi & rating sengaja dibikin gampang dihitung.
DATA = [
    {
        "judul": "Alpha",
        "genre": "aksi",
        "tahun": 2000,
        "durasi": 100,
        "rating": 8.0,
        "catatan": "",
    },
    {
        "judul": "Bravo",
        "genre": "aksi",
        "tahun": 2010,
        "durasi": 140,
        "rating": 7.0,
        "catatan": "",
    },
    {
        "judul": "Golf",
        "genre": "aksi",
        "tahun": 2002,
        "durasi": 110,
        "rating": 8.5,
        "catatan": "",
    },
    {
        "judul": "Charlie",
        "genre": "drama",
        "tahun": 2010,
        "durasi": 120,
        "rating": 9.0,
        "catatan": "",
    },
    {
        "judul": "Delta",
        "genre": "drama",
        "tahun": 1995,
        "durasi": 90,
        "rating": 6.5,
        "catatan": "sedih banget",
    },
    {
        "judul": "Echo",
        "genre": "komedi",
        "tahun": 2005,
        "durasi": 80,
        "rating": 8.5,
        "catatan": "",
    },
    {
        "judul": "Foxtrot",
        "genre": "komedi",
        "tahun": 2015,
        "durasi": 95,
        "rating": 7.5,
        "catatan": "",
    },
]

# Data khusus buat nguji pencarian biner yang nyari awal judul.
DATA_AWAL = [
    {
        "judul": "The Shining",
        "genre": "horor",
        "tahun": 1980,
        "durasi": 144,
        "rating": 9.0,
        "catatan": "",
    },
    {
        "judul": "The Dark Knight",
        "genre": "aksi",
        "tahun": 2008,
        "durasi": 152,
        "rating": 9.0,
        "catatan": "",
    },
    {
        "judul": "The Avengers",
        "genre": "aksi",
        "tahun": 2012,
        "durasi": 143,
        "rating": 8.0,
        "catatan": "",
    },
]


class TestParseAngka(unittest.TestCase):
    def test_angka_biasa(self):
        self.assertEqual(film.parse_angka("120"), 120)

    def test_pakai_titik(self):
        self.assertEqual(film.parse_angka("1.200"), 1200)

    def test_pakai_spasi(self):
        self.assertEqual(film.parse_angka(" 95 "), 95)

    def test_bukan_angka(self):
        self.assertIsNone(film.parse_angka("dua puluh"))

    def test_kosong_ditolak(self):
        self.assertIsNone(film.parse_angka(""))

    def test_nol_ditolak(self):
        self.assertIsNone(film.parse_angka("0"))


class TestParseRating(unittest.TestCase):
    def test_desimal_titik(self):
        self.assertEqual(film.parse_rating("8.5"), 8.5)

    def test_desimal_koma(self):
        self.assertEqual(film.parse_rating("8,5"), 8.5)

    def test_bulat(self):
        self.assertEqual(film.parse_rating("9"), 9.0)

    def test_batas_atas(self):
        self.assertEqual(film.parse_rating("10"), 10.0)

    def test_melebihi_sepuluh(self):
        self.assertIsNone(film.parse_rating("11"))

    def test_negatif(self):
        self.assertIsNone(film.parse_rating("-1"))

    def test_bukan_angka(self):
        self.assertIsNone(film.parse_rating("bagus"))


class TestFormatDurasi(unittest.TestCase):
    def test_jam_dan_menit(self):
        self.assertEqual(film.format_durasi(152), "2 j 32 m")

    def test_persis_jam(self):
        self.assertEqual(film.format_durasi(120), "2 j")

    def test_menit_saja(self):
        self.assertEqual(film.format_durasi(45), "45 m")


class TestBulatkanNilai(unittest.TestCase):
    """CLI harus nunjukkin angka yang sama kayak versi JS di web."""

    def test_setengah_ke_atas(self):
        self.assertEqual(film.bulatkan_nilai(8.25), 8.3)

    def test_setengah_lain(self):
        self.assertEqual(film.bulatkan_nilai(8.75), 8.8)

    def test_bukan_setengah(self):
        self.assertEqual(film.bulatkan_nilai(8.24), 8.2)

    def test_nol(self):
        self.assertEqual(film.bulatkan_nilai(0), 0.0)


class TestSkorGenre(unittest.TestCase):
    def test_kata_genre_langsung(self):
        self.assertEqual(film.skor_genre(DATA, "hantu", "horor"), 4)

    def test_ketemu_di_judul(self):
        self.assertEqual(film.skor_genre(DATA, "alpha", "aksi"), 2)

    def test_kata_kosong_nol(self):
        self.assertEqual(film.skor_genre(DATA, "", "aksi"), 0)

    def test_kata_nggak_nyambung(self):
        self.assertEqual(film.skor_genre(DATA, "qqq", "komedi"), 0)


class TestSaranKategori(unittest.TestCase):
    def test_hantu_ke_horor(self):
        self.assertEqual(film.saran_kategori(DATA, "hantu")[0][0], "horor")

    def test_nama_genre_langsung(self):
        self.assertEqual(film.saran_kategori(DATA, "drama")[0][0], "drama")

    def test_nggak_nyambung_kosong(self):
        self.assertEqual(film.saran_kategori(DATA, "zzzz"), [])

    def test_skor_menurun(self):
        hasil = film.saran_kategori(DATA, "a")
        skor = [nilai for _, nilai in hasil]
        self.assertEqual(skor, sorted(skor, reverse=True))

    def test_genrenya_valid_saja(self):
        hasil = film.saran_kategori(DATA, "a")
        self.assertTrue(all(genre in film.GENRE_VALID for genre, _ in hasil))


class TestCariFilm(unittest.TestCase):
    def test_filter_genre(self):
        hasil = film.cari_film(DATA, "aksi")
        self.assertEqual([i["judul"] for i in hasil], ["Alpha", "Bravo", "Golf"])

    def test_genre_none_ambil_semua(self):
        self.assertEqual(len(film.cari_film(DATA, None)), len(DATA))

    def test_genre_nggak_ada(self):
        self.assertEqual(film.cari_film(DATA, "dokumenter"), [])


class TestUrutkan(unittest.TestCase):
    def test_rating_turun(self):
        hasil = film.urutkan(DATA, "rating")
        nilai = [i["rating"] for i in hasil]
        self.assertEqual(nilai, sorted(nilai, reverse=True))
        self.assertEqual(hasil[0]["judul"], "Charlie")

    def test_tahun_turun(self):
        hasil = film.urutkan(DATA, "tahun")
        nilai = [i["tahun"] for i in hasil]
        self.assertEqual(nilai, sorted(nilai, reverse=True))
        self.assertEqual(hasil[0]["tahun"], 2015)

    def test_durasi_naik(self):
        hasil = film.urutkan(DATA, "durasi")
        nilai = [i["durasi"] for i in hasil]
        self.assertEqual(nilai, sorted(nilai))
        self.assertEqual(hasil[0]["judul"], "Echo")

    def test_judul_abjad(self):
        hasil = film.urutkan(DATA, "judul")
        nama = [i["judul"] for i in hasil]
        self.assertEqual(nama, sorted(nama))

    def test_urutan_nggak_dikenal(self):
        with self.assertRaises(ValueError):
            film.urutkan(DATA, "bioskop")

    def test_nggak_mengubah_asli(self):
        sebelum = [i["judul"] for i in DATA]
        film.urutkan(DATA, "rating")
        self.assertEqual([i["judul"] for i in DATA], sebelum)


class TestCariJudulBiner(unittest.TestCase):
    def test_awal_judul(self):
        hasil = film.cari_judul_biner(DATA, "b")
        self.assertEqual([i["judul"] for i in hasil], ["Bravo"])

    def test_lebih_dari_satu_awal_sama(self):
        hasil = film.cari_judul_biner(DATA_AWAL, "the")
        self.assertEqual(len(hasil), 3)

    def test_ketemu_tapi_bukan_urut_awal(self):
        # DATA nggak tersorting, tapi biner search tetap harus ketemu.
        hasil = film.cari_judul_biner(DATA, "foxtrot")
        self.assertEqual([i["judul"] for i in hasil], ["Foxtrot"])

    def test_nggak_ketemu(self):
        self.assertEqual(film.cari_judul_biner(DATA, "xyz"), [])

    def test_kata_kosong(self):
        self.assertEqual(film.cari_judul_biner(DATA, ""), [])


class TestCariKataKunci(unittest.TestCase):
    def test_dari_judul(self):
        hasil = film.cari_kata_kunci(DATA, "delta")
        self.assertEqual([i["judul"] for i in hasil], ["Delta"])

    def test_case_insensitive(self):
        hasil = film.cari_kata_kunci(DATA, "DELTA")
        self.assertEqual([i["judul"] for i in hasil], ["Delta"])

    def test_dari_tahun(self):
        hasil = film.cari_kata_kunci(DATA, "2010")
        self.assertEqual(len(hasil), 2)

    def test_dari_catatan(self):
        hasil = film.cari_kata_kunci(DATA, "sedih")
        self.assertEqual([i["judul"] for i in hasil], ["Delta"])

    def test_kata_kosong(self):
        self.assertEqual(film.cari_kata_kunci(DATA, ""), [])


class TestRekomendasiSerupa(unittest.TestCase):
    def test_nggak_balikin_dirinya_sendiri(self):
        hasil = film.rekomendasi_serupa(DATA, DATA[0])  # Alpha
        self.assertNotIn("Alpha", [i["judul"] for i in hasil])

    def test_genre_harus_sama(self):
        hasil = film.rekomendasi_serupa(DATA, DATA[0])  # aksi
        self.assertTrue(all(i["genre"] == "aksi" for i in hasil))

    def test_rating_paling_dekat_duluan(self):
        # Alpha rating 8.0. Golf (8.5) selisihnya 0.5, Bravo (7.0) selisihnya 1.0.
        hasil = film.rekomendasi_serupa(DATA, DATA[0])
        self.assertEqual(hasil[0]["judul"], "Golf")

    def test_batasi_jumlah(self):
        hasil = film.rekomendasi_serupa(DATA, DATA[0], jumlah=1)
        self.assertEqual(len(hasil), 1)


class TestPaketMarathon(unittest.TestCase):
    def test_total_paling_mendekati_batas(self):
        # 3 film terbaik: Charlie 120 + Alpha 100 + Echo 80 = 300 (rating 25.5),
        # seri sama Golf 110 + Alpha 100 + Delta 90 = 300 tapi ratingnya lebih kecil.
        paket = film.paket_marathon(DATA, 300)
        self.assertEqual(paket["total"], 300)
        self.assertEqual(paket["sisa"], 0)
        self.assertEqual(paket["rating_rata"], 8.5)

    def test_mundur_ke_jumlah_lebih_sedikit(self):
        # 150 menit nggak muat 2 film (pendek 80+90=170), jadi jatuh ke 1 film.
        paket = film.paket_marathon(DATA, 150)
        self.assertEqual(len(paket["film"]), 1)
        self.assertEqual(paket["total"], 140)

    def test_batas_kekecilan(self):
        self.assertIsNone(film.paket_marathon(DATA, 70))

    def test_data_kosong(self):
        self.assertIsNone(film.paket_marathon([], 300))


class TestDataFile(unittest.TestCase):
    """Baca data_film.json beneran buat mastiin datanya sehat."""

    @classmethod
    def setUpClass(cls):
        cls.data = film.muat_data()

    def test_file_ada(self):
        self.assertTrue(os.path.exists(film.NAMA_FILE))

    def test_jumlah_film(self):
        self.assertEqual(len(self.data), 36)

    def test_field_lengkap(self):
        for item in self.data:
            self.assertEqual(
                set(item.keys()),
                {"judul", "genre", "tahun", "durasi", "rating", "catatan"},
            )

    def test_genre_valid(self):
        for item in self.data:
            self.assertIn(item["genre"], film.GENRE_VALID)

    def test_judul_unik(self):
        judul = [item["judul"].lower() for item in self.data]
        self.assertEqual(len(judul), len(set(judul)))

    def test_tahun_wajar(self):
        for item in self.data:
            self.assertTrue(1888 <= item["tahun"] <= 2100)

    def test_durasi_positif(self):
        for item in self.data:
            self.assertGreater(item["durasi"], 0)

    def test_rating_dalam_rentang(self):
        for item in self.data:
            self.assertTrue(0 <= item["rating"] <= 10)

    def test_semua_genre_terisi(self):
        for genre in film.GENRE_VALID:
            self.assertTrue(film.cari_film(self.data, genre))


if __name__ == "__main__":
    unittest.main()
