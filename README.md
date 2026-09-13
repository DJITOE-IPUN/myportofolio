Nama    :   Michael Evan Putra Nugroho

NPM     :   2506616674

Kelas   :   PBP C

# Portfolio Website

## Ringkasan Perubahan 1 (Tugas 1)
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

---

### Tugas 2

#### Ringkasan Perubahan 2 (Tugas 2)
Pada Tugas 2 ini, dilakukan pengembangan arsitektur Model-View-Template (MVT) pada Django:
- **Pembuatan Model Data Baru**: Menambahkan model `Education` dan `Award` pada `main/models.py` dengan Primary Key berupa `UUIDField` serta penggunaan atribut `choices`.
- **Migrasi Basis Data**: Membikin dan menerapkan berkas migrasi basis data untuk skema model baru.
- **Routing & Views Modular**: Membuat *view* `show_education` dan `show_awards` serta mendaftarkan *named routes* pada `main/urls.py`.
- **Template DTL & Dynamic Rendering**: Membuat berkas `education.html` dan `awards.html` menggunakan perulangan `{% for %}`, `{% empty %}` state, serta navigasi terintegrasi `{% url %}`.
- **Unit Testing**: Menuliskan 6 kasus pengujian unit pada `main/tests.py` untuk menguji aksesibilitas URL, render *template*, kondisi data ada, dan *empty state*.

---

#### Pertanyaan Reflektif

1. **Alur Permintaan MVT (HTTP Request to Response)**
   Ketika pengguna membuka halaman baru (misalnya `/education/`), alur yang terjadi adalah:
   - **HTTP Request**: Peramban mengirimkan *request* HTTP GET ke server Django.
   - **Proyek `urls.py`**: Django menerima *request* dan mencocokkan awalan URL, lalu mengarahkannya ke `main/urls.py`.
   - **Aplikasi `urls.py`**: `main/urls.py` mencocokkan jalur `'education/'` dengan *named route* `show_education` dan memanggil fungsi *view* terkait.
   - **View (`views.py`)**: Fungsi `show_education` mengeksekusi *query* ke basis data via model (`Education.objects.all()`).
   - **Model (`models.py`)**: Model mengambil data riwayat pendidikan dari tabel basis data dan mengembalikannya ke *view* sebagai *QuerySet*.
   - **Template & Context**: *View* memasukkan data tersebut ke dalam *context dictionary* dan merender *template* `education.html`.
   - **HTTP Response**: Django menyusun HTML akhir yang telah diisi data dinamis dan mengembalikannya ke peramban pengguna.

2. **Pentingnya Model vs Hardcoded Data**
   Menyimpan data di dalam model (*database*) jauh lebih unggul dibandingkan menulisnya secara *hardcoded* di berkas HTML karena:
   - **Pemisahan Tanggung Jawab (*Separation of Concerns*)**: Logika tampilan (HTML) terpisah dari pengelolaan data (DB).
   - **Kemudahan Pemeliharaan (*Maintainability*)**: Penambahan atau perubahan data dapat dilakukan secara dinamis melalui Admin Panel tanpa perlu mengubah struktur kode atau melakukan *re-deploy*.
   - **Skalabilitas (*Scalability*)**: Data yang tersimpan di model dapat diolah kembali untuk berbagai kebutuhan lain (API REST, penyaringan data, atau ekspor laporan) secara efisien.

3. **Perbedaan `makemigrations` dan `migrate`**
   - **`makemigrations`**: Berfungsi untuk mendeteksi perubahan pada `models.py` dan membuat berkas rancangan/skenario migrasi (*blueprint*) di folder `migrations/` tanpa mengubah basis data fisik.
   - **`migrate`**: Berfungsi mengeksekusi berkas migrasi tersebut dan menerapkan perubahan skema secara nyata ke dalam tabel basis data (`db.sqlite3`).
   - **Contoh Kasus**: Ketika kita menambahkan *field* baru `field_of_study` pada model `Education` atau mengubah Primary Key menjadi `UUIDField`, kita wajib menjalankan `python manage.py makemigrations` untuk membuat cetak biru perubahan, lalu `python manage.py migrate` untuk memperbarui struktur tabel di basis data.

---

#### AI Disclosure

* **Tools AI yang Digunakan**: Gemini (Google AI).
* **Link / Public Share Log Chat**: [Tempelkan Tautan Share Chat Gemini Kamu di Sini]

##### 1. Strategi Prompting & Arsitektur Interaksi
Dalam pengerjaan Tugas 2 ini, diterapkan metode **Iterative System-Constrained Prompting** bertahap. AI dilarang menghasilkan *boilerplate code* secara masif tanpa persetujuan struktur. Pembatasan dilakukan dengan memberikan parameter ketat:
- **Constraint Domain**: Mengunci arsitektur pada pola Django Model-View-Template (MVT) murni tanpa pustaka pihak ketiga.
- **Code Ownership Enforcer**: Menolak kode yang *over-engineered* agar seluruh fungsi pada `models.py`, `views.py`, dan `tests.py` dapat dipertanggungjawabkan 100% saat sesi *demo* lab bersama asisten dosen.
- **Data Integrity**: Mengharuskan penggunaan *real-world dataset* riwayat akademis dan penghargaan tanpa teks pengisi (*placeholder/lorem ipsum*).

##### 2. Kronologi Log Prompting & Alur Kerja
| Tahap | Tujuan Prompt | Luaran AI (*Output*) | Tindakan / Evaluasi Pengembang |
| --- | --- | --- | --- |
| **01** | Eksplorasi penambahan model data baru melampaui batas minimal tugas. | Rekomendasi 2 model baru: `Education` dan `Award`. | **Disetujui**: Menambah 2 model sekaligus untuk menargetkan nilai optimal fungsionalitas. |
| **02** | Perancangan Primary Key dan enkapsulasi tipe data. | Generasi model Django dasar dengan `UUIDField` dan `choices`. | **Koreksi Manual**: Memperbaiki nilai `default` pada `CharField(choices=...)` agar tidak konflik saat migrasi. |
| **03** | Penyusunan *routing* URL dan *views* modular. | Fungsi `show_education` & `show_awards` serta pendaftaran *named routes*. | **Disetujui**: Mengintegrasikan `app_name = 'main'` dan pengarahan *template*. |
| **04** | Penyelarasan antarmuka *template* HTML DTL. | Kode DTL `{% for %}`, `{% empty %}`, dan `{% url %}`. | **Koreksi Manual**: Mengenkapsulasi *empty state* ke dalam `<article class="experience-card">` agar visual konsisten. |
| **05** | Pembentukan pengujian otomatis (*Unit Testing*). | Draf awal kelas tes di `main/tests.py`. | **Koreksi Manual**: Perbaikan *field mismatch* dan penghapusan variabel non-eksisten pada objek tes. |

##### 3. Analisis Keterbatasan AI
Meskipun AI sangat mempercepat generasi struktur dasar kode, ditemukan 3 keterbatasan teknis utama yang berisiko menggagalkan pengujian jika tidak dikoreksi secara manual:

1. **Halusinasi Skema Model pada Unit Testing (Model Field Mismatch)**
   - *Keterbatasan AI*: Saat membuatkan draf unit tes untuk model `Experience`, AI berasumsi bahwa skema model memiliki atribut `ended_at` serta metode penanganan status yang belum pernah didefinisikan di `models.py`. Selain itu, pembuatan objek sampel di tes mengecualikan *field* wajib seperti `organization` dan `date_range`.
   - *Dampak*: Menjalankan `python manage.py test` menghasilkan *error* `TypeError` dan `ValidationError` yang menghentikan jalannya tes otomatis.
   - *Perbaikan Manual*: Mengisolasi kelas pengujian menjadi 4 kelas modular (`MainViewTest`, `ExperienceTest`, `EducationTest`, `AwardTest`), melengkapi seluruh *required fields* pada metode `setUp()`, dan menghapus pemanggilan atribut `ended_at`.

2. **Inkonsistensi Render Choice Field pada Template DTL**
   - *Keterbatasan AI*: AI secara bawaan langsung memanggil variabel atribut choice secara mentah di DTL (`{{ experience.category }}` atau `{{ edu.degree }}`).
   - *Dampak*: Antarmuka menampilkan *raw database key* (misal: `"bachelor"` atau `"part-time"`) yang kaku dan tidak ramah pengguna, bukannya string terbaca (misal: `"S1 / Bachelor Degree"` atau `"Part-Time"`).
   - *Perbaikan Manual*: Mengganti pemanggilan variabel DTL secara manual menggunakan metode bawaan Django `.get_FOO_display` (contoh: `{{ edu.get_degree_display }}` dan `{{ experience.get_category_display }}`).

3. **Kerusakan Structural Layout pada State Kosong (*Empty State Broken Structure*)**
   - *Keterbatasan AI*: Pada berkas `experience.html`, AI meletakkan tag `{% empty %}` di luar elemen pembungkus kartu HTML (`<article class="experience-card">`).
   - *Dampak*: Saat tabel basis data kosong, pesan *empty state* ditampilkan sebagai teks polos tanpa *styling* CSS *Tactical Tech*, merusak simetri visual yang ada pada `education.html` dan `awards.html`.
   - *Perbaikan Manual*: Merombak hirarki DOM HTML di `experience.html` dengan memasukkan tag DTL `{% empty %}` ke dalam pembungkus `<article class="experience-card">` dan menerapkan kelas CSS `.empty-state`.

##### 4. Ringkasan Intervensi Kode Mandiri (*Code Ownership*)
Seluruh pembaruan backend pada `main/models.py`, pemisahan jalur routing `main/urls.py`, eksekusi migrasi basis data (`0002_...`), penyelarasan DTL antarmuka, hingga kelulusan 6 pengujian unit otomatis di `main/tests.py` telah diverifikasi dan disesuaikan 100% secara manual untuk memastikan keandalan aplikasi di lingkungan lokal.

##### 5. AI Chat Log
*Selengkapnya dapat dilihat pada tautan berikut:* ristek.link/AI-chat-log-tugas-2