from django.forms import ModelForm, TextInput, Textarea, URLInput
from main.models import Education, Project, Award, Experience


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "field_of_study",
            "date_range",
            "description",
        ]

        labels = {
            "institution": "Institusi Pendidikan",
            "degree": "Jenjang Pendidikan",
            "field_of_study": "Program Studi / Jurusan",
            "date_range": "Masa Studi",
            "description": "Deskripsi",
        }

        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia, SMA Taruna Nusantara, dll.",
                    "maxlength": 255,
                }
            ),
            "degree": TextInput(
                attrs={
                    "placeholder": "S1 / Sarjana, High School Diploma, dll.",
                    "maxlength": 255,
                }
            ),
            "field_of_study": TextInput(
                attrs={
                    "placeholder": "Ilmu Komputer, MIPA, dll.",
                    "maxlength": 255,
                }
            ),
            "date_range": TextInput(
                attrs={
                    "placeholder": "2025 - Present, 2022 - 2025",
                    "maxlength": 100,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pencapaian atau aktivitas selama masa studi...",
                    "rows": 3,
                }
            ),
        }


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://example.com/image.png",
                }
            ),
        }


class AwardForm(ModelForm):
    class Meta:
        model = Award
        fields = [
            "title",
            "issuer",
            "date_awarded",
            "description",
        ]

        labels = {
            "title": "Nama Penghargaan",
            "issuer": "Penyelenggara / Pemberi",
            "date_awarded": "Tahun / Tanggal Penerimaan",
            "description": "Deskripsi Prestasi",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Juara 1 Hackathon / Best Paper Award",
                    "maxlength": 255,
                }
            ),
            "issuer": TextInput(
                attrs={
                    "placeholder": "Fasilkom UI / Kementerian Kominfo",
                    "maxlength": 255,
                }
            ),
            "date_awarded": TextInput(
                attrs={
                    "placeholder": "2026",
                    "maxlength": 100,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Deskripsikan detail pencapaian atau kategori lomba...",
                    "rows": 3,
                }
            ),
        }