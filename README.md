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
* **Link / Public Share Log Chat**: ristek.link/AI-chat-log-tugas-2

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

---

### Tugas 3: Form & Data Delivery

#### Ringkasan Perubahan 3 (Tugas 3)
Pada Tugas 3, dilakukan pengayaan fungsionalitas aplikasi portofolio melalui penanganan formulir interaktif (*Form Handling*), operasi manipulasi data (Create, Update, Delete), serta penyediaan *endpoint* pengiriman data berformat JSON:

1. **Refactoring Template Inheritance (`base.html`)**: Mengkonsolidasikan elemen `<head>`, *navigation bar* global (Profile, Experience, Education, Awards, Projects), dan *footer* ke dalam `base.html` sebagai *parent template* utama. Seluruh *child templates* merelokasi struktur kode dengan `{% extends 'base.html' %}` dan `{% block content %}`.
2. **Pengembangan `ModelForm` Modular**: Mengimplementasikan kelas `EducationForm`, `ProjectForm`, dan `AwardForm` pada `main/forms.py` yang terhubung langsung dengan model ORM Django. Setiap form dilengkapi penyesuaian *widgets*, *labels*, dan *placeholders*.
3. **Penerapan Fungsi CRUD (Create, Update, Delete)**:
   - **Create**: Fungsi `create_education`, `create_project`, dan `create_award` untuk memproses penambahan data baru via formulir `POST`.
   - **Update (Edit)**: Fungsi `edit_education`, `edit_project`, dan `edit_award` yang memanfaatkan argumen `instance` pada `ModelForm` untuk mengubah data yang sudah ada.
   - **Delete**: Fungsi `delete_education`, `delete_project`, dan `delete_award` yang diproses secara aman menggunakan metode `POST` dengan CSRF protection.
4. **Komponen Konfirmasi Hapus UI (`popover` Modal)**: Mengintegrasikan komponen *modal dialog* berbasis fitur *native* HTML5 `popover` di `templates/components/` untuk konfirmasi penghapusan data secara interaktif tanpa ketergantungan pustaka JavaScript luar.
5. **JSON Data Delivery Endpoints**: Menyediakan *endpoint* serialisasi data berformat JSON pada `main/views.py` (`show_json_education`, `show_json_projects`, `show_json_awards`, serta `show_json_by_id`) yang memanfaatkan `django.core.serializers`.
6. **Pengujian Unit Otomatis (Unit Testing)**: Memperbarui suite pengujian pada `main/tests.py` untuk menguji penambahan data via form `POST`, penghapusan data, serta validasi *Content-Type: application/json* pada *endpoint* JSON.

---

#### Pertanyaan Reflektif

1. **Keunggulan `ModelForm` Dibandingkan Form HTML Manual**
   Menggunakan `ModelForm` Django memiliki beberapa keunggulan utama dibandingkan membuat form HTML manual dari awal:
   - **Otomatisasi Validasi & Binding Data**: `ModelForm` secara otomatis memetakan tipe data, aturan validasi, serta batasan (*constraints*) dari model ORM (seperti `max_length` atau `required`) tanpa perlu menuliskan pengecekan manual di *view*.
   - **Eksekusi Penyimpanan Efisien (`form.save()`)**: `ModelForm` menyediakan metode `.save()` yang langsung mengabstraksi pembuatan objek ORM baru atau pembaruan objek `instance` tanpa perlu melakukan ekstraksi variabel `request.POST.get()` satu per satu.
   - **Pencegahan Redundansi Kode (*DRY Principle*)**: Struktur bidang (*fields*) pada form cukup didefinisikan satu kali merujuk ke kelas modelnya, sehingga perubahan skema di `models.py` akan otomatis terefleksi pada form.
   - **Sistem Error Handling Terintegrasi**: `ModelForm` secara otomatis menangkap *validation error* dan meneruskannya ke *template* HTML melalui `{{ field.errors }}` untuk ditampilkan ke pengguna.

2. **Mekanisme Proteksi CSRF (`{% csrf_token %}`) pada Django**
   - **Cara Kerja**: Ketika *template* merender tag `{% csrf_token %}`, Django menghasilkan nilai token rahasia yang acak (*cryptographically secure token*) dan menyisipkannya sebagai *hidden input* di dalam formulir HTML. Token yang sama juga disimpan dalam *cookie* peramban pengguna. Saat formulir dikirimkan melalui metode `POST`, middleware Django (`CsrfViewMiddleware`) mencocokkan token dari formulir dengan token pada *cookie*.
   - **Pentingnya Proteksi CSRF**: Serangan *Cross-Site Request Forgery* (CSRF) terjadi ketika situs berbahaya mengeksekusi aksi tak terotorisasi atas nama pengguna yang sedang terautentikasi. Proteksi CSRF memastikan bahwa setiap permintaan mutasi data (`POST`, `PUT`, `DELETE`) benar-benar berasal dari antarmuka resmi aplikasi kita, bukan dari Domain pihak ketiga.

3. **Perbedaan Pengiriman Data Format HTML vs Format JSON**
   - **Format HTML (Server-Side Rendering)**:
   - *Karakteristik*: Server memproses data ORM, memasukkannya ke *template* DTL, dan mengembalikan dokumen HTML utuh yang siap ditampilkan langsung oleh peramban.
     - *Kelebihan*: Ramah SEO, memindahkan beban komputasi antarmuka ke server, dan tidak memerlukan pemrosesan JavaScript tambahan di *client*.
     - *Kapan Digunakan*: Tampilan halaman web statis/dinamis standar yang dibaca langsung oleh pengguna manusia (*human interface*).
   - **Format JSON (Data Delivery Endpoint)**:
   - *Karakteristik*: Server hanya mengirimkan struktur data mentah (*raw key-value data*) terkompresi tanpa elemen dekorasi atau *styling* HTML.
     - *Kelebihan*: Ukuran data jauh lebih ringan, bersifat independen dari tampilan visual, serta dapat dikonsumsi oleh berbagai jenis *client* (seperti aplikasi *frontend* JavaScript/React/Vue, aplikasi seluler Flutter, atau integrasi API pihak ketiga).
   - *Kapan Digunakan*: Pembangunan aplikasi SPA (*Single Page Application*), interaktivitas AJAX/Fetch asynchronous di *frontend*, integrasi aplikasi *mobile*, atau penyediaan layanan Web API REST.

---

#### AI Disclosure

* **Tools AI yang Digunakan**: Gemini (Google AI).
* **Link / Public Share Log Chat**: ristek.link/AI-chat-log-tugas-3

##### 1. Strategi Prompting & Arsitektur Interaksi
Pengembangan Tugas 3 menerapkan pendekatan **Iterative System-Constrained Prompting**. Perintah dibatasi oleh instruksi eksplisit agar AI tidak menghasilkan kode *over-engineered* atau menggunakan pustaka JavaScript pihak ketiga yang kompleks, sehingga seluruh alur MVT, *forms*, dan *routing* tetap mudah dipahami dan dipertanggungjawabkan secara penuh saat sesi *demo* lab.

##### 2. Kronologi Log Prompting Utama

| Tahap | Tujuan Prompt | Luaran AI (*Output*) | Tindakan & Evaluasi Pengembang |
| --- | --- | --- | --- |
| **01** | Refactoring *template inheritance* dengan `base.html`. | Draf `base.html` serta pembersihan tag duplikat di `index.html`, `experience.html`, dll. | **Disetujui**: Mengonsolidasikan `<head>`, navigasi 5 menu, dan *footer*. |
| **02** | Perancangan `ModelForm` untuk Education, Project, dan Award. | Generasi kelas `EducationForm`, `ProjectForm`, dan `AwardForm` di `main/forms.py`. | **Koreksi Manual**: Memperbaiki kunci *widget* `"date-range"` menjadi `"date_range"` dan mengubah `URLInput` menjadi `TextInput`. |
| **03** | Penyusunan fungsi CRUD dan *JSON endpoints* di `views.py`. | Fungsi *create*, *edit*, *delete*, dan *serializers JSON*. | **Koreksi Manual**: Mengoreksi nama *import* `AwardsForm` menjadi `AwardForm`. |
| **04** | Pendaftaran URL routing di `main/urls.py`. | Jalur URL CRUD dan JSON Data Delivery. | **Koreksi Manual**: Mengubah *converter* `<uuid:id>` menjadi `<str:id>` agar fleksibel menerima ID integer maupun string UUID. |
| **05** | Penyusunan *Unit Test* untuk Form POST, Delete, dan JSON. | Kasus pengujian unit di `main/tests.py`. | **Disetujui**: Menjaga struktur *class* tes lama dan menambahkan metode pengujian fungsionalitas baru. |

##### 3. Analisis Keterbatasan AI

Dalam proses pengembangan, ditemukan 3 keterbatasan teknis yang berhasil diidentifikasi dan dikoreksi secara manual (*Human-in-the-Loop*):

1. **Inkompatibilitas URL Path Converter (`<uuid:id>` vs Primary Key Auto-Increment)**
   - *Keterbatasan AI*: AI secara otomatis menggenerasi jalur URL pada `main/urls.py` menggunakan tipe *converter* `<uuid:id>` untuk seluruh parameter ID.
   - *Dampak*: Apabila skema model Django menggunakan Primary Key integer *auto-increment* bawaan (`1`, `2`, `3`), URL converter `<uuid:id>` akan menolak permintaan HTTP dan mengembalikan galat `404 Not Found`.
   - *Perbaikan Manual*: Mengubah seluruh *converter* URL parameter ID pada `main/urls.py` dari `<uuid:id>` menjadi `<str:id>` agar aplikasi dapat menangani ID berupa string UUID maupun angka integer.

2. **Isu Flexibilitas Tag Action pada Form HTML Reusable**
   - *Keterbatasan AI*: AI memberikan atribut `action="{% url 'main:create_education' %}"` secara keras (*hardcoded*) di dalam tag `<form>` pada berkas *template* form.
   - *Dampak*: Berkas *template* form tersebut menjadi tidak bisa digunakan kembali (*non-reusable*) untuk fungsi Ubah/Edit data (`edit_education`), karena form akan selalu mengirimkan data `POST` ke *endpoint create*.
   - *Perbaikan Manual*: Mengosongkan atribut `action` (menjadi `<form method="post">`) sehingga formulir secara fleksibel mengirimkan data `POST` ke URL tempat form tersebut sedang dirender, memungkinkan 1 berkas *template* yang sama digunakan untuk operasi *Create* maupun *Update*.

3. **Inkonsistensi Impor Kelas Form pada Views (`AwardsForm` vs `AwardForm`)**
   - *Keterbatasan AI*: AI menghasilkan pernyataan impor `from main.forms import AwardsForm` (menggunakan akhiran 's') pada `main/views.py`, padahal kelas yang terdefinisi pada `forms.py` bernama `AwardForm`.
   - *Dampak*: Server Django mengalami galat `ImportError` yang membuat seluruh aplikasi *crash* saat dijalankan.
   - *Perbaikan Manual*: Mengubah nama *import* di `main/views.py` menjadi `AwardForm` secara manual agar selaras dengan definisi kelas pada `main/forms.py`.

##### 4. Ringkasan Intervensi Kode Mandiri (*Code Ownership*)
Seluruh refactoring DTL `base.html`, perbaikan *bug widget* pada `forms.py`, penyelarasan *routing* `urls.py`, hingga pembaruan pengujian unit pada `main/tests.py` telah diverifikasi, dites via `python manage.py test`, dan dipastikan berjalan 100% aman di lingkungan lokal.

---

### Tugas 4: Authentication, Session, and Cookies Implementation

#### Ringkasan Perubahan 4 (Tugas 4)
Pada Tugas 4, dilakukan implementasi sistem autentikasi, manajemen sesi, cookies, serta otorisasi berjenjang berbasis 4 tingkat hak akses (*4-tier authorization*) pada situs portofolio:

1. **Relasi Model Data & Migrasi (`stars`)**: Menambahkan *field* `stars` menggunakan `ManyToManyField(User)` pada model `Project` di `main/models.py` untuk mengimplementasikan fitur *star* interaktif per pengguna.
2. **Implementasi Otorisasi 4 Peran (*Server-Side Checks*)**:
   - **Pengunjung (Guest)**: Bebas membaca data. Mengakses fungsi mutasi (*create/edit/delete*) atau *star* memicu *redirect* otomatis ke halaman Login (`@login_required`).
   - **Pengguna Biasa (Logged-in User)**: Dapat membaca data dan memberi/membatalkan *star* (maksimal 1 *star* per proyek). Mencoba eksekusi CRUD ditolak dengan HTTP `403 Forbidden`.
   - **Editor**: Memiliki hak Pengguna Biasa serta dapat mengubah data (`edit_project`), namun ditolak HTTP `403 Forbidden` jika mencoba menambah (`create`) atau menghapus (`delete`) data. Hak akses dikelola via Django Group `Editor`.
   - **Pemilik Portofolio (Superuser)**: Memiliki hak akses penuh untuk membuat (`create_project`), mengubah (`edit_project`), menghapus (`delete_project`), serta memberikan/membatalkan *star*.
3. **Komponen UI Interaktif & DTL Conditional Rendering**:
   - Membangun komponen reusable `templates/components/project_star.html` dengan form `POST` dan token `{% csrf_token %}`.
   - Mengatur kondisional DTL `{% if %}` di `templates/projects.html` untuk menampilkan tombol Tambah/Hapus (Superuser saja), Edit (Editor & Superuser), dan Star (Logged-in User).
4. **Keamanan & Integritas Endpoint API JSON**: Memastikan *endpoint* JSON (`show_json_projects`) tetap berjalan aman tanpa mengekspos *field* sensitif pengguna seperti *password hash* atau token sesi.
5. **Pengujian Unit Otomatis (Unit Testing)**: Memperbarui suite pengujian pada `main/tests.py` dengan memanfaatkan `self.client.force_login(self.superuser)` agar seluruh 23 kasus uji lulus berstatus `OK`.

---

#### Pertanyaan Reflektif
> *Catatan: Pertanyaan reflektif untuk pekan ini dihilangkan sesuai instruksi resmi Tugas 4.*

---

#### AI Disclosure

* **Tools AI yang Digunakan**: Gemini (Google AI).
* **Link / Public Share Log Chat**: ristek.link/AI-chat-log-tugas-4

##### 1. Strategi Prompting & Arsitektur Interaksi
Pengembangan Tugas 4 menerapkan pendekatan **Iterative System-Constrained Prompting**. Perintah dibatasi oleh instruksi eksplisit agar AI tidak menghasilkan kode *over-engineered* atau mengabaikan pengecekan keamanan di sisi server (*server-side authorization*). Seluruh alur otorisasi 4 peran, relasi ORM `ManyToManyField`, serta suite pengujian diselaraskan agar 100% dipahami dan dapat dipertanggungjawabkan saat sesi *demo* lab bersama asisten dosen.

##### 2. Kronologi Log Prompting Utama

| Tahap | Tujuan Prompt | Luaran AI (*Output*) | Tindakan & Evaluasi Pengembang |
| --- | --- | --- | --- |
| **01** | Penambahan relasi `ManyToManyField` pada model `Project`. | Penambahan *field* `stars = models.ManyToManyField(User)` pada `main/models.py`. | **Koreksi Manual**: Membedakan `related_name='starred_projects'` agar tidak bentrok (*clash*) dengan model lain. |
| **02** | Perancangan logika otorisasi 4 peran dan `toggle_star` pada `views.py`. | Fungsi `toggle_star`, *helper* `check_is_editor`, serta pengecekan `HttpResponseForbidden`. | **Disetujui**: Mengintegrasikan dekorator `@login_required` dan `@require_POST` pada aksi mutasi. |
| **03** | Pembentukan komponen UI DTL & penyesuaian `projects.html`. | Berkas `project_star.html` dan pengondisian DTL `{% if %}` di `projects.html`. | **Disetujui**: Menyembunyikan tombol aksi sensitif sesuai peran pengguna secara dinamis. |
| **04** | Pendaftaran URL routing di `main/urls.py`. | Path `projects/<uuid:id>/star/` dan penyesuaian rute CRUD. | **Disetujui**: Menjaga konsistensi penamaan rute *named routes*. |
| **05** | Perbaikan *Unit Testing* akibat proteksi otorisasi. | Pembaruan `main/tests.py` dengan `force_login`. | **Koreksi Manual**: Mengubah nilai *degree* pada `EducationTest` dari string deskriptif ke kunci *choices* ORM (`bachelor`). |

##### 3. Analisis Keterbatasan AI

Dalam proses pengembangan Tugas 4, ditemukan 3 keterbatasan AI yang berhasil diidentifikasi dan dikoreksi secara manual (*Human-in-the-Loop*):

1. **Bentrokan Nama Relasi Balik (*Reverse Accessor Clash* / `fields.E304`)**
   - *Keterbatasan AI*: Saat menyarankankan relasi `ManyToManyField(User)`, AI menggunakan nilai `related_name='starred_projects'` yang identik pada model `Project` dan model `Experience`.
   - *Dampak*: Menjalankan `python manage.py makemigrations` memicu galat `SystemCheckError: (fields.E304) Reverse accessor clashes`, yang menghentikan proses migrasi basis data.
   - *Perbaikan Manual*: Mengisolasi `related_name` secara eksplisit menjadi `'starred_projects'` khusus pada model `Project` dan `'starred_experiences'` pada model `Experience`.

2. **Kegagalan Validasi Choice Field pada Unit Testing (`AssertionError: 200 != 302`)**
   - *Keterbatasan AI*: AI memberikan nilai string `"High School"` pada payload test `Education`, padahal skema model memerlukan kunci *choices* yang terdefinisi pada ORM (`"bachelor"` / `"high_school"`).
   - *Dampak*: `form.is_valid()` bernilai `False` saat POST request diuji, menyebabkan server mengembalikan status `200 OK` (render ulang form berpesan error) alih-alih `302 Found` (redirect sukses).
   - *Perbaikan Manual*: Mengoreksi nilai payload pada `test_create_education_post` menjadi kunci pilihan yang valid (`"bachelor"`) sehingga seluruh 23 unit test lulus sempurna.

3. **Inkompatibilitas Akses Sesi pada Test Client Tanpa Autentikasi**
   - *Keterbatasan AI*: AI menggenerasi draf awal unit test tanpa memperhitungkan dampak penambahan proteksi otorisasi server-side (`@login_required` dan `HttpResponseForbidden`).
   - *Dampak*: Seluruh test POST `create_*` dan `delete_*` mengalami kegagalan (*6 failures*) karena di-redirect ke login atau ditolak dengan HTTP 403.
   - *Perbaikan Manual*: Menambahkan pembuatan akun superuser (`User.objects.create_superuser`) dan mengeksekusi `self.client.force_login(self.superuser)` pada metode `setUp()` di kelas tes terkait.

##### 4. Ringkasan Intervensi Kode Mandiri (*Code Ownership*)
Seluruh penambahan skema ORM `stars`, pembuatan logika *helper authorization* di `views.py`, penyusunan komponen UI DTL `project_star.html`, hingga penyelarasan 23 kasus uji unit pada `main/tests.py` telah diverifikasi dan dites 100% secara manual di lingkungan lokal.