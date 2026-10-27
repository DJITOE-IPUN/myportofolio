from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import Experience, Education, Award, Project


class MainViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_main_url_is_accessible_and_uses_correct_template(self):
        """Memastikan URL utama / dapat diakses dan merender template index.html"""
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_nonexistent_page_returns_404(self):
        """Memastikan akses ke URL yang tidak terdaftar mengembalikan status 404"""
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)


class ExperienceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            organization="Fasilkom UI",
            date_range="Aug 2026 – Present",
            category="part-time",
            description="Membantu mahasiswa memahami pengembangan web.",
            is_ongoing=True,
        )

    def test_experience_model_str(self):
        """Memastikan method __str__ pada model Experience berfungsi dengan benar"""
        self.assertEqual(str(self.experience), "Asisten Dosen PBP - Fasilkom UI")
        self.assertEqual(self.experience.category, "part-time")

    def test_experience_page_renders_data(self):
        """Memastikan halaman experience menampilkan data yang ada di database"""
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.organization)

    def test_empty_experience_page(self):
        """Memastikan pesan empty state muncul jika belum ada data Experience"""
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No sorties logged yet.")

    def test_experience_json_by_id(self):
        """Memastikan JSON endpoint by ID mengembalikan data JSON untuk Experience"""
        response = self.client.get(reverse("main:show_json_by_id", kwargs={"model_type": "experience", "id": self.experience.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")


class EducationTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Buat user superuser untuk pengujian yang membutuhkan hak akses penuh
        self.superuser = User.objects.create_superuser(
            username="admin_test", password="password123"
        )
        self.client.force_login(self.superuser)

    def test_education_url_is_accessible_and_uses_correct_template(self):
        """Memastikan URL /education/ dapat diakses dan menggunakan template education.html"""
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_empty_state(self):
        """Memastikan pesan kondisi kosong tampil ketika belum ada data Education"""
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "No qualifications logged yet.")

    def test_education_renders_data(self):
        """Memastikan data Education yang dibuat muncul di halaman HTML"""
        Education.objects.create(
            institution="Universitas Indonesia",
            degree="bachelor",
            field_of_study="Computer Science",
            date_range="2025 – Present",
            description="Fokus pada rekayasa perangkat lunak dan arsitektur sistem.",
        )
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Universitas Indonesia")

    def test_create_education_post(self):
        """Memastikan penambahan data Education via Form (POST) berfungsi untuk Superuser"""
        response = self.client.post(reverse("main:create_education"), {
            "institution": "SMA Taruna Nusantara",
            "degree": "bachelor",
            "field_of_study": "MIPA",
            "date_range": "2022 - 2025",
            "description": "Lulus dengan predikat baik.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Education.objects.count(), 1)

    def test_delete_education_post(self):
        """Memastikan penghapusan data Education via POST berfungsi untuk Superuser"""
        edu = Education.objects.create(
            institution="UI",
            degree="Bachelor",
            field_of_study="CS",
            date_range="2025"
        )
        response = self.client.post(reverse("main:delete_education", kwargs={"id": edu.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Education.objects.count(), 0)

    def test_json_education_endpoint(self):
        """Memastikan endpoint JSON Data Delivery untuk Education berfungsi"""
        response = self.client.get(reverse("main:show_json_education"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")


class AwardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="admin_test_award", password="password123"
        )
        self.client.force_login(self.superuser)

    def test_awards_url_is_accessible_and_uses_correct_template(self):
        """Memastikan URL /awards/ dapat diakses dan menggunakan template awards.html"""
        response = self.client.get(reverse("main:show_awards"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "awards.html")

    def test_awards_empty_state(self):
        """Memastikan pesan kondisi kosong tampil ketika belum ada data Award"""
        response = self.client.get(reverse("main:show_awards"))
        self.assertContains(response, "No awards on the rack yet.")

    def test_awards_renders_data(self):
        """Memastikan data Award yang dibuat muncul di halaman HTML"""
        Award.objects.create(
            title="Juara 1 Hackathon",
            issuer="Fasilkom UI",
            category="competition",
            date_awarded="Aug 2026",
            description="Penghargaan atas inovasi sistem pertahanan terintegrasi.",
        )
        response = self.client.get(reverse("main:show_awards"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Juara 1 Hackathon")

    def test_create_award_post(self):
        """Memastikan penambahan data Award via Form (POST) berfungsi untuk Superuser"""
        response = self.client.post(reverse("main:create_award"), {
            "title": "Best Paper Award",
            "issuer": "Kementerian Kominfo",
            "date_awarded": "2026",
            "description": "Paper riset sistem pertahanan.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Award.objects.count(), 1)
        # no category sent: the ribbon family falls back to "honor"
        self.assertEqual(Award.objects.get().category, "honor")

    def test_delete_award_post(self):
        """Memastikan penghapusan data Award via POST berfungsi untuk Superuser"""
        award = Award.objects.create(
            title="Kompetisi UI",
            issuer="UI",
            date_awarded="2026"
        )
        response = self.client.post(reverse("main:delete_award", kwargs={"id": award.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Award.objects.count(), 0)

    def test_json_awards_endpoint(self):
        """Memastikan endpoint JSON Data Delivery untuk Award berfungsi"""
        response = self.client.get(reverse("main:show_json_awards"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")


class ProjectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="admin_test_project", password="password123"
        )
        self.client.force_login(self.superuser)

    def test_projects_url_is_accessible_and_uses_correct_template(self):
        """Memastikan URL /projects/ dapat diakses dan menggunakan template projects.html"""
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_projects_empty_state(self):
        """Memastikan pesan kondisi kosong tampil ketika belum ada data Project"""
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No projects in the hangar yet.")

    def test_create_project_post(self):
        """Memastikan penambahan data Project via Form (POST) berfungsi untuk Superuser"""
        response = self.client.post(reverse("main:create_project"), {
            "title": "Defense Tech Radar",
            "description": "Aplikasi radar simulasi.",
            "tech_stack": "Django, Python",
            "project_url": "https://github.com/test/radar",
            "project_image_url": "https://example.com/img.png",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 1)

    def test_delete_project_post(self):
        """Memastikan penghapusan data Project via POST berfungsi untuk Superuser"""
        project = Project.objects.create(
            title="Web Portofolio",
            description="Deskripsi proyek",
            tech_stack="Django"
        )
        response = self.client.post(reverse("main:delete_project", kwargs={"id": project.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 0)

    def test_json_projects_endpoint(self):
        """Memastikan endpoint JSON Data Delivery untuk Project berfungsi"""
        response = self.client.get(reverse("main:show_json_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

class HomepageAfterburnerTest(TestCase):
    """Homepage: Unclassified CV data, radar counts and GitHub telemetry fallback."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_homepage_includes_records_for_one_page_cv(self):
        """Memastikan homepage memuat data Experience, Project, Education dan Award untuk CV Unclassified"""
        Experience.objects.create(
            title="Sortie Uji", organization="Fasilkom UI", location="Depok",
            date_range="2026", category="volunteer", is_ongoing=True,
        )
        Project.objects.create(title="Radar Uji", description="Deskripsi", tech_stack="Django, Python")
        Education.objects.create(
            institution="Universitas Indonesia", degree="bachelor",
            field_of_study="Ilmu Komputer", date_range="2025 – Present",
        )
        Award.objects.create(title="Pita Uji", issuer="UI", category="honor", date_awarded="2026")

        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        for text in ("Sortie Uji", "Radar Uji", "Universitas Indonesia", "Pita Uji"):
            self.assertContains(response, text)
        self.assertEqual(response.context["stack_list"], ["Django", "Python"])

    def test_homepage_keeps_last_login_cookie(self):
        """Memastikan informasi sesi login terakhir (cookie) tetap tampil di homepage"""
        self.client.cookies["last_login"] = "2026-10-25 21:00:00"
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "2026-10-25 21:00:00")

    def test_telemetry_is_none_without_token(self):
        """Memastikan telemetry GitHub mengembalikan None jika GITHUB_TOKEN tidak diatur"""
        from unittest import mock
        from main.telemetry import get_github_telemetry
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": ""}):
            self.assertIsNone(get_github_telemetry())

    def test_telemetry_shapes_github_payload(self):
        """Memastikan data GraphQL GitHub diolah menjadi trace, top speed, dan readouts"""
        from unittest import mock
        from main.telemetry import get_github_telemetry

        def week(start, counts):
            return {"contributionDays": [
                {"date": f"2026-10-{start + i:02d}", "contributionCount": c} for i, c in enumerate(counts)
            ]}

        payload = {"data": {"user": {
            "followers": {"totalCount": 9},
            "repositories": {"totalCount": 14},
            "latest": {"nodes": [{"name": "myportofolio", "url": "https://github.com/x/y",
                                  "pushedAt": "2026-10-25T10:00:00Z"}]},
            "contributionsCollection": {"contributionCalendar": {
                "totalContributions": 12,
                "weeks": [week(4, [1, 1]), week(11, [5, 3]), week(18, [2])],
            }},
        }}}
        fake = mock.Mock(status_code=200)
        fake.json.return_value = payload
        fake.raise_for_status.return_value = None

        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}), \
                mock.patch("main.telemetry.requests.post", return_value=fake) as post:
            data = get_github_telemetry()
            get_github_telemetry()  # second call is served from the cache

        self.assertEqual(post.call_count, 1)
        self.assertEqual(data["total"], 12)
        self.assertEqual(data["repos"], 14)
        self.assertEqual(data["top_speed"], 8)
        self.assertEqual(str(data["top_week"]), "2026-10-11")
        self.assertEqual(len(data["trace_points"].split()), 3)
        self.assertEqual(data["last_repo"], "myportofolio")

    def test_telemetry_failure_falls_back_to_none(self):
        """Memastikan homepage tetap aman jika GitHub gagal dihubungi"""
        from unittest import mock
        from main.telemetry import get_github_telemetry
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}), \
                mock.patch("main.telemetry.requests.post", side_effect=Exception("offline")):
            self.assertIsNone(get_github_telemetry())


class AfterburnerHelpersTest(TestCase):
    """Presentation helpers behind Sorties, Qualifications and the Ribbon rack."""

    def test_parse_period_reads_common_formats(self):
        """Memastikan rentang tanggal teks bebas (EN/ID) terbaca dengan benar"""
        from datetime import date
        from main.afterburner import parse_period
        today = date(2026, 10, 26)

        p = parse_period("Aug 2026 – Present", today=today)
        self.assertEqual(p.start, date(2026, 8, 1))
        self.assertTrue(p.ongoing)
        self.assertEqual(p.months, 3)

        p = parse_period("2022 - 2025", today=today)
        self.assertFalse(p.ongoing)
        self.assertEqual((p.start.year, p.end.year), (2022, 2025))

        p = parse_period("Agustus 2024 s/d Sekarang", today=today)
        self.assertEqual(p.start, date(2024, 8, 1))
        self.assertTrue(p.ongoing)

        p = parse_period("2025 – 2029", today=today)  # expected graduation
        self.assertTrue(p.ongoing)

        p = parse_period("", today=today)
        self.assertIsNone(p.start)

    def test_sorties_are_in_flight_order(self):
        """Memastikan Sorties diurutkan dari yang paling lama dan menghitung flight time"""
        from main.afterburner import build_sorties, flight_path
        Experience.objects.create(title="Baru", organization="B", location="Depok",
                                  date_range="Aug 2026 – Present", category="volunteer", is_ongoing=True,
                                  kit="Django, Figma")
        Experience.objects.create(title="Lama", organization="A", location="Depok",
                                  date_range="Jan 2025 – Jun 2025", category="internship", is_ongoing=False)
        sorties = build_sorties(Experience.objects.all())
        self.assertEqual([s["obj"].title for s in sorties], ["Lama", "Baru"])
        self.assertEqual(sorties[0]["code"], "SRT-01")
        self.assertEqual(sorties[0]["flight_time"], "6 mo")
        self.assertEqual(sorties[0]["outcome"], "Returned to base")
        self.assertEqual(sorties[1]["kit"], ["Django", "Figma"])
        path = flight_path(2)
        self.assertEqual(path["width"], 200)
        self.assertTrue(path["d"].startswith("M 0 50"))

    def test_qualification_semester_progress(self):
        """Memastikan semester berjalan dihitung dari awal tahun ajaran (Agustus)"""
        from datetime import date
        from main.afterburner import build_qualifications
        Education.objects.create(institution="Universitas Indonesia", degree="bachelor",
                                 field_of_study="Ilmu Komputer", date_range="2025 – Present")
        Education.objects.create(institution="SMA", degree="secondary_school",
                                 field_of_study="MIPA", date_range="2022 – 2025")
        quals = build_qualifications(Education.objects.all(), today=date(2026, 10, 26))
        self.assertEqual(quals[0]["obj"].institution, "Universitas Indonesia")
        self.assertEqual(quals[0]["status"], "In training")
        self.assertEqual((quals[0]["semester"], quals[0]["semesters"]), (3, 8))
        self.assertEqual(quals[1]["status"], "Qualified")

    def test_ribbons_are_symmetric_and_stable(self):
        """Memastikan pita penghargaan simetris, konsisten, dan merah sesuai kategori"""
        from main.afterburner import ribbon_stripes, build_rack
        award = Award.objects.create(title="Juara 1", issuer="UI", category="competition", date_awarded="2026")
        stripes = ribbon_stripes(award)
        self.assertEqual(stripes, ribbon_stripes(award))
        self.assertIn("r-red", {s["cls"] for s in stripes})
        for s in stripes:
            self.assertGreaterEqual(s["x"], 0)
            self.assertLessEqual(s["x"] + s["w"], 100)
        honor = Award.objects.create(title="Mention", issuer="UI", category="honor", date_awarded="2025")
        self.assertNotIn("r-red", {s["cls"] for s in ribbon_stripes(honor)})

        for i in range(3):
            Award.objects.create(title=f"Extra {i}", issuer="UI", category="academic", date_awarded="2024")
        items, rack = build_rack(Award.objects.all())
        self.assertEqual([len(row) for row in rack], [2, 3])  # short row on top
        self.assertEqual(items[0]["obj"].title, "Juara 1")    # newest first


class AfterburnerPagesTest(TestCase):
    """Themed pages, the experience star route and the error pages."""

    def setUp(self):
        self.user = User.objects.create_user(username="pilot", password="password123")

    def test_experience_star_route_stars_experience(self):
        """Memastikan route star Experience benar-benar memberi star pada Experience (bukan Project)"""
        exp = Experience.objects.create(title="Sortie", organization="UI", location="Depok",
                                        date_range="2026", category="volunteer", is_ongoing=True)
        self.client.force_login(self.user)
        url = reverse("main:toggle_experience_star", kwargs={"id": exp.id})

        response = self.client.post(url)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertEqual(exp.stars.count(), 1)

        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.json(), {"starred": False, "count": 0})

    def test_project_star_returns_json_for_ajax(self):
        """Memastikan star Project via AJAX mengembalikan JSON"""
        project = Project.objects.create(title="Radar", description="x", tech_stack="Django")
        self.client.force_login(self.user)
        response = self.client.post(reverse("main:toggle_project_star", kwargs={"id": project.id}),
                                    HTTP_ACCEPT="application/json")
        self.assertEqual(response.json(), {"starred": True, "count": 1})

    def test_themed_pages_render_records(self):
        """Memastikan halaman Sorties, Qualifications, dan Ribbon rack menampilkan data"""
        Experience.objects.create(title="Staf Ahli Partnership", organization="Open House Fasilkom UI",
                                  location="Depok", date_range="Aug 2026 – Present", category="volunteer",
                                  is_ongoing=True, kit="Notion, Canva")
        Education.objects.create(institution="Universitas Indonesia", degree="bachelor",
                                 field_of_study="Ilmu Komputer", date_range="2025 – Present")
        Award.objects.create(title="Juara 1 Hackathon", issuer="Fasilkom UI", category="competition",
                             date_awarded="Aug 2026")
        self.assertContains(self.client.get(reverse("main:show_experience")), "SRT-01")
        self.assertContains(self.client.get(reverse("main:show_experience")), "Notion")
        self.assertContains(self.client.get(reverse("main:show_education")), "In training")
        response = self.client.get(reverse("main:show_awards"))
        self.assertContains(response, "CIT-01")
        self.assertContains(response, 'class="r-red"')

    def test_maintenance_controls_hidden_from_visitors(self):
        """Memastikan tombol tambah/hapus hanya terlihat oleh pemilik portofolio"""
        Education.objects.create(institution="UI", degree="bachelor", field_of_study="CS", date_range="2025")
        response = self.client.get(reverse("main:show_education"))
        self.assertNotContains(response, reverse("main:create_education"))
        self.assertNotContains(response, "Scrub rating")

    def test_cool_wall_renders(self):
        """Memastikan halaman Cool Wall dapat diakses"""
        response = self.client.get(reverse("main:show_coolwall"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coolwall.html")
        self.assertContains(response, "Sub-zero")

    def test_non_owner_gets_themed_403(self):
        """Memastikan user biasa mendapat halaman 403 bertema saat mencoba menambah data"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("main:create_education"))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Clearance insufficient.", status_code=403)

    def test_404_page_when_debug_is_off(self):
        """Memastikan halaman 404 bertema tampil saat DEBUG=False"""
        from django.test import override_settings
        with override_settings(DEBUG=False):
            response = self.client.get("/target-yang-hilang/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Target lost.", status_code=404)

    def test_login_page_renders_clearance_panel(self):
        """Memastikan halaman login dan register memakai panel clearance"""
        self.assertContains(self.client.get(reverse("main:login")), "AUTH-01")
        self.assertContains(self.client.get(reverse("main:register")), "AUTH-02")


class EducationAjaxTest(TestCase):
    """AJAX Education: JSON list with permissions, search, and create_education_ajax."""

    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="password123")
        self.visitor = User.objects.create_user(username="visitor", password="password123")

    def test_json_reads_years_from_date_range(self):
        """Memastikan JSON education menurunkan start/end year dari date_range dan menyertakan status"""
        Education.objects.create(institution="Universitas Indonesia", degree="bachelor",
                                 field_of_study="Ilmu Komputer", date_range="2025 – Present")
        data = self.client.get(reverse("main:show_json_education")).json()
        edu = data["educations"][0]
        self.assertEqual((edu["start_year"], edu["end_year"]), ("2025", "Present"))
        self.assertEqual(edu["status"], "In training")
        self.assertFalse(data["user_permissions"]["is_superuser"])

    def test_json_search_by_institution(self):
        """Memastikan pencarian AJAX berdasarkan nama institusi"""
        Education.objects.create(institution="Universitas Indonesia", degree="bachelor", field_of_study="CS", date_range="2025")
        Education.objects.create(institution="SMA Taruna", degree="secondary_school", field_of_study="MIPA", date_range="2022 – 2025")
        data = self.client.get(reverse("main:show_json_education"), {"institution": "taruna"}).json()
        self.assertEqual([e["institution"] for e in data["educations"]], ["SMA Taruna"])

    def test_create_education_ajax(self):
        """Memastikan create_education_ajax: 201 untuk pemilik, 400 dengan errors, 403 untuk user biasa"""
        url = reverse("main:create_education_ajax")
        payload = {"institution": "Universitas Indonesia", "degree": "bachelor",
                   "field_of_study": "Ilmu Komputer", "date_range": "2025 – Present"}

        self.client.force_login(self.visitor)
        self.assertEqual(self.client.post(url, payload).status_code, 403)

        self.client.force_login(self.owner)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Education.objects.count(), 1)

        response = self.client.post(url, {"degree": "bachelor"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("institution", response.json()["errors"])

    def test_projects_json_has_permissions(self):
        """Memastikan JSON projects menyertakan user_permissions untuk frontend"""
        Project.objects.create(title="Radar", description="x", tech_stack="Django")
        self.client.force_login(self.owner)
        data = self.client.get(reverse("main:show_json_projects"), {"title": "rad"}).json()
        self.assertEqual(data["projects"][0]["title"], "Radar")
        self.assertTrue(data["user_permissions"]["is_superuser"])


class HomepageAfterburnerTest(TestCase):
    """Homepage: Unclassified CV data, radar counts and GitHub telemetry fallback."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_homepage_includes_records_for_one_page_cv(self):
        """Memastikan homepage memuat data Experience, Project, Education dan Award untuk CV Unclassified"""
        Experience.objects.create(
            title="Sortie Uji", organization="Fasilkom UI", location="Depok",
            date_range="2026", category="volunteer", is_ongoing=True,
        )
        Project.objects.create(title="Radar Uji", description="Deskripsi", tech_stack="Django, Python")
        Education.objects.create(
            institution="Universitas Indonesia", degree="bachelor",
            field_of_study="Ilmu Komputer", date_range="2025 – Present",
        )
        Award.objects.create(title="Pita Uji", issuer="UI", category="honor", date_awarded="2026")

        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        for text in ("Sortie Uji", "Radar Uji", "Universitas Indonesia", "Pita Uji"):
            self.assertContains(response, text)
        self.assertEqual(response.context["stack_list"], ["Django", "Python"])

    def test_homepage_keeps_last_login_cookie(self):
        """Memastikan informasi sesi login terakhir (cookie) tetap tampil di homepage"""
        self.client.cookies["last_login"] = "2026-10-25 21:00:00"
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "2026-10-25 21:00:00")

    def test_telemetry_is_none_without_token(self):
        """Memastikan telemetry GitHub mengembalikan None jika GITHUB_TOKEN tidak diatur"""
        from unittest import mock
        from main.telemetry import get_github_telemetry
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": ""}):
            self.assertIsNone(get_github_telemetry())

    def test_telemetry_shapes_github_payload(self):
        """Memastikan data GraphQL GitHub diolah menjadi trace, top speed, dan readouts"""
        from unittest import mock
        from main.telemetry import get_github_telemetry

        def week(start, counts):
            return {"contributionDays": [
                {"date": f"2026-10-{start + i:02d}", "contributionCount": c} for i, c in enumerate(counts)
            ]}

        payload = {"data": {"user": {
            "followers": {"totalCount": 9},
            "repositories": {"totalCount": 14},
            "latest": {"nodes": [{"name": "myportofolio", "url": "https://github.com/x/y",
                                  "pushedAt": "2026-10-25T10:00:00Z"}]},
            "contributionsCollection": {"contributionCalendar": {
                "totalContributions": 12,
                "weeks": [week(4, [1, 1]), week(11, [5, 3]), week(18, [2])],
            }},
        }}}
        fake = mock.Mock(status_code=200)
        fake.json.return_value = payload
        fake.raise_for_status.return_value = None

        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}), \
                mock.patch("main.telemetry.requests.post", return_value=fake) as post:
            data = get_github_telemetry()
            get_github_telemetry()  # second call is served from the cache

        self.assertEqual(post.call_count, 1)
        self.assertEqual(data["total"], 12)
        self.assertEqual(data["repos"], 14)
        self.assertEqual(data["top_speed"], 8)
        self.assertEqual(str(data["top_week"]), "2026-10-11")
        self.assertEqual(len(data["trace_points"].split()), 3)
        self.assertEqual(data["last_repo"], "myportofolio")

    def test_telemetry_failure_falls_back_to_none(self):
        """Memastikan homepage tetap aman jika GitHub gagal dihubungi"""
        from unittest import mock
        from main.telemetry import get_github_telemetry
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}), \
                mock.patch("main.telemetry.requests.post", side_effect=Exception("offline")):
            self.assertIsNone(get_github_telemetry())
