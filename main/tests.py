from django.test import TestCase, Client
from django.urls import reverse
from main.models import Experience, Education, Award


class MainViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_main_url_is_accessible_and_uses_correct_template(self):
        """Memastikan URL utama / dapat diakses dan merender template index.html"""
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

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
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")

    def test_empty_experience_page(self):
        """Memastikan pesan empty state muncul jika belum ada data Experience"""
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")


class EducationTest(TestCase):
    def setUp(self):
        self.client = Client()

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
        self.assertContains(response, "S1 / Bachelor Degree")


class AwardTest(TestCase):
    def setUp(self):
        self.client = Client()

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
        self.assertContains(response, "Fasilkom UI")