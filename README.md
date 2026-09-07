Nama    :   Michael Evan Putra Nugroho

NPM     :   2506616674

Kelas   :   PBP C

# Portfolio Website

## Ringkasan Perubahan Proyek (Tugas 1)
Pada Tugas 1 ini, beberapa pembaruan utama yang dilakukan meliputi:
- **Pembaruan Data Diri**: Mengganti seluruh data contoh dari Tutorial 01 pada section *About Me* dengan identitas asli (Nama: Michael Evan Putra Nugroho, NPM: 2506616674, foto profil, dan bio ringkas).
- **Penambahan Section "Experiences"**: Menambahkan section baru dengan elemen semantik HTML5 (`<section>` dan `<article>`) yang berisi 8 riwayat pengalaman organisasi dan kepanitiaan riil.
- **Kustomisasi Tema & Styling CSS3**: Merombak total visual halaman dari *template* bawaan menjadi tema *Aviation & Tactical Tech (Dark Mode)* menggunakan variabel CSS `:root`, font *Space Grotesk* dan *Fira Code*, serta layout Flexbox yang responsif.

---

## Cara Menjalankan Proyek
1. Pastikan Python 3 dan Virtual Environment sudah aktif.
2. Jalankan perintah server lokal Django di terminal:
   ```bash
   python manage.py runserver

---

### Tugas 1

#### Pertanyaan Reflektif

1. **Penggunaan Elemen Semantik HTML5**
   Ya, saya menggunakan elemen semantik HTML5 seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<dl>`, dan `<footer>`. Elemen semantik ini membantu membagi struktur halaman menjadi blok-blok logis yang bermakna:
   - `<section>` digunakan untuk memisahkan area utama portofolio (`#profile` dan `#experiences`).
   - `<article>` membungkus setiap item riwayat pengalaman secara mandiri (`experience-card`), sehingga struktur data memiliki konteks utuh.
   - `<nav>` dan `<dl>` mempertegas fungsi elemen navigasi serta daftar metadata (NPM dan Program Studi).
   
   Elemen semantik ini meningkatkan keterbacaan kode (*code readability*), mempermudah proses *debugging*, serta mendukung aksesibilitas (*screen reader*) dan SEO tanpa bergantung pada tumpukan tag `<div>` generik.

2. **Tantangan Tata Letak & Strategi CSS Responsive**
   Tantangan tata letak utama muncul saat mentransisikan tampilan 2-kolom pada *hero section* (teks profil dan foto) serta menyelaraskan baris header kartu pengalaman (peran dan tanggal) agar tidak saling berbenturan (*overlapping*) di layar seluler yang sempit.

   **Strategi Evaluasi & Penyesuaian Layout:**
   - **Tumpukan Vertikal (*Stacked Layout*)**: Menggunakan *media query* (`@media (max-width: 600px)`), tata letak *CSS Grid* 2-kolom diubah menjadi 1-kolom vertikal menggunakan `grid-template-areas`.
   - **Prioritas Skala Visual**: Ukuran avatar foto diperkecil (maksimal 200px) agar tidak menghabiskan ruang layar utama sebelum pengguna membaca biodata.
   - **Flexbox Wrapper**: Mengatur atribut header pengalaman menggunakan `display: flex; justify-content: space-between; flex-wrap: wrap;` sehingga rentang tanggal otomatis berpindah ke bawah dengan rapi saat lebar layar menyempit.

3. **Batasan Static Web & Rencana Fungsionalitas Dinamis**
   **Batasan yang Dirasakan:**
   Sebagai *static web* murni, seluruh data profil dan riwayat pengalaman masih tertulis secara keras (*hardcoded*) di dalam file HTML. Jika ada pembaruan data, file kode harus diedit dan di-*deploy* ulang secara manual. Selain itu, belum ada fitur interaktif seperti penyaringan (*filtering*) pengalaman atau formulir kontak.

   **Fungsionalitas Dinamis yang Ingin Ditambahkan (Rencana Belum Bersifat Final):**
   - **Integration Django MVT**: Mengintegrasikan basis data (SQLite/PostgreSQL) agar data pengalaman dan proyek dapat dikelola secara dinamis via *admin panel*.
   - **Filtering & Interaktivitas**: Menambahkan fitur penyaring riwayat pengalaman berdasarkan kategori (Organisasi, Kepanitiaan, atau Asisten) menggunakan JavaScript.
   - **Formulir Kontak**: Menyediakan formulir pesan interaktif yang tersimpan ke basis data backend.

---

#### AI Disclosure

* **Tools yang Digunakan**: Gemini (Google AI).
* **Strategi Prompting**:
  - Menggunakan *iterative step-by-step prompting* (bertahap) dengan menetapkan target kemampuan (skor 3.5) agar kode tetap bersih, efisien, dan mudah dijelaskan saat sesi *demo* lab.
  - Memberikan instruksi spesifik dengan melampirkan file bawaan Tutorial 01 dan data pengalaman riil tanpa menggunakan teks *placeholder*.
* **Bagian Kode/Dokumentasi yang Dibantu AI**:
  1. Penulisan struktur semantik HTML5 untuk *section* `#experiences` menggunakan tag `<section>` dan `<article>`.
  2. Penyusunan tema CSS *Aviation & Tactical Tech (Dark Mode)* memanfaatkan variabel CSS `:root`, Flexbox, dan CSS Grid responsif.

* **Analisis Kritis Keterbatasan AI & Koreksi Manual**:
  - **Keterbatasan AI**: AI sempat menyarankan perubahan tata letak yang terlalu kompleks (seperti *Asymmetric Dashboard Sidebar* dan efek *JavaScript timeline*).
  - **Koreksi Manual**: 
    1. Menolak perubahan layout yang berlebihan dan mempertahankan struktur tata letak *Single-Column Hero + Flexbox Cards* agar kodenya intuitif dan 100% dipahami.
    2. Menyederhanakan properti CSS agar murni menggunakan variabel `:root` dan Flexbox bawaan tanpa *dependency* luar.
    3. Memasukkan dan merapikan seluruh data riwayat organisasi asli (OSIS SMA Taruna Nusantara, Open House Fasilkom UI, COMPFEST, ARUNG, DDP 0, dll) secara akurat.

* **AI Chat Log**:
  *Selengkapnya dapat dilihat pada tautan berikut:* ristek.link/AI-chat-log-tugas-1