"""Ubah BLOG_POST.md jadi BLOG_POST.html yang siap dibuka di browser.

Judul, deskripsi, dan tanggal diambil otomatis dari isi markdown, jadi
tinggal edit BLOG_POST.md lalu jalanin script ini lagi.

Jalanin: python convert_blog.py
"""

import html
import io
import re

import markdown

md_path = "BLOG_POST.md"
html_path = "BLOG_POST.html"
tanggal = "15 Oktober 2026"

REPO = "https://github.com/Rolin-data/Rekomendasi-Film"

with io.open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()


def ambil_judul(teks):
    """Judul diambil dari heading H1 pertama."""
    cocok = re.search(r"^#\s+(.+)$", teks, re.MULTILINE)
    return cocok.group(1).strip() if cocok else "Blog Post"


def ambil_deskripsi(teks, panjang_maks=160):
    """Deskripsi diambil dari paragraf teks pertama setelah judul."""
    for paragraf in teks.split("\n\n"):
        paragraf = paragraf.strip()
        if not paragraf or paragraf.startswith(("#", "```", "-", "*", ">", "|", "!")):
            continue
        bersih = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", paragraf)  # buang link
        bersih = re.sub(r"[*`_]", "", bersih)
        bersih = re.sub(r"\s+", " ", bersih).strip()
        if len(bersih) > panjang_maks:
            bersih = bersih[:panjang_maks].rsplit(" ", 1)[0] + "..."
        return bersih
    return "Tulisan teknis soal program rekomendasi film."


judul = ambil_judul(md_text)
deskripsi = ambil_deskripsi(md_text)

body = markdown.markdown(md_text, extensions=["fenced_code", "tables", "codehilite"])

html_full = (
    """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>"""
    + html.escape(judul)
    + """</title>
<meta name="description" content=\""""
    + html.escape(deskripsi, quote=True)
    + """\">
<meta property="og:title" content=\""""
    + html.escape(judul, quote=True)
    + """\">
<meta property="og:description" content=\""""
    + html.escape(deskripsi, quote=True)
    + """\">
<meta property="og:type" content="article">
<style>
:root{--bg:#f8fafc;--card:#fff;--line:#e5e7eb;--teks:#111827;--muted:#6b7280;--link:#4f46e5}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--teks);font:17px/1.75 system-ui,Segoe UI,Roboto,sans-serif}
nav.bar{background:#0f172a;color:#e2e8f0}
nav.bar .dalam{max-width:800px;margin:auto;padding:14px 20px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;font-size:14px}
nav.bar .nama{font-weight:600;color:#fff;margin-right:auto;letter-spacing:.2px}
nav.bar a{color:#c7d2fe;text-decoration:none}
nav.bar a:hover{text-decoration:underline}
main{max-width:800px;margin:28px auto;background:var(--card);padding:36px 32px;border-radius:14px;box-shadow:0 10px 30px rgba(2,6,23,.06)}
h1{font-size:30px;line-height:1.3;margin-top:0}
h2{font-size:23px;line-height:1.35;margin-top:34px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:19px;line-height:1.4;margin-top:26px}
pre,code{font-family:ui-monospace,Consolas,monospace}
pre{background:#0f172a;color:#e2e8f0;padding:16px;border-radius:8px;overflow:auto;font-size:14px;line-height:1.5}
code{background:#eef2f7;color:#4338ca;padding:2px 5px;border-radius:4px;font-size:.92em}
pre code{background:transparent;color:inherit;padding:0;border-radius:0}
table{border-collapse:collapse;width:100%;margin:16px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left}
th{background:#f9fafb}
ul,ol{padding-left:24px}
li{margin:6px 0}
a{color:var(--link)}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
footer.kaki{max-width:800px;margin:0 auto 44px;padding:0 20px;color:var(--muted);font-size:13px;line-height:1.6}
footer.kaki a{color:#4f46e5}
@media(max-width:640px){body{font-size:16px}main{margin:12px;padding:22px 18px;border-radius:10px}h1{font-size:25px}h2{font-size:21px}}
</style>
</head>
<body>
<nav class="bar">
  <div class="dalam">
    <span class="nama">Rekomendasi Film</span>
    <a href="index.html">Demo web</a>
    <a href=\""""
    + REPO
    + """\">Repo GitHub</a>
  </div>
</nav>
<main>
"""
    + body
    + """
</main>
<footer class="kaki">
  Ditulis oleh <strong>Rolin Stallin</strong> &middot; """
    + tanggal
    + """ &middot;
  Kode lengkapnya di <a href=\""""
    + REPO
    + """\">github.com/Rolin-data/Rekomendasi-Film</a>.
</footer>
</body>
</html>"""
)

with io.open(html_path, "w", encoding="utf-8") as f:
    f.write(html_full)

print("OK", html_path, len(html_full))
print("Judul    :", judul)
print("Deskripsi:", deskripsi)
