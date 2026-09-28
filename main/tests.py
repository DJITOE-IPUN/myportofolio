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
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

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
        self.assertContains(response, "Belum ada riwayat pendidikan")

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
        self.assertContains(response, "Belum ada penghargaan")

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
        self.assertContains(response, "Belum ada proyek")

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