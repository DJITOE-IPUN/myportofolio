from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, URLInput, Select
from django.utils.html import strip_tags
from main.models import Education, Project, Award, Experience


class EducationForm(ModelForm):
    def clean_degree(self):
        degree = self.cleaned_data.get("degree", "").strip()
        normalized = {
            "bachelor": "bachelor",
            "bachelors": "bachelor",
            "s1": "bachelor",
            "sarjana": "bachelor",
            "secondary school": "secondary_school",
            "high school": "secondary_school",
            "sma": "secondary_school",
            "smk": "secondary_school",
            "diploma": "diploma",
            "d3": "diploma",
            "master": "master",
            "s2": "master",
            "magister": "master",
        }
        return normalized.get(degree.lower(), degree)

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
            "institution": "Institution",
            "degree": "Level",
            "field_of_study": "Field of study",
            "date_range": "Period",
            "description": "Notes",
        }

        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "degree": Select(choices=Education.DEGREE_CHOICES),
            "field_of_study": TextInput(
                attrs={
                    "placeholder": "Computer Science",
                    "maxlength": 255,
                }
            ),
            "date_range": TextInput(
                attrs={
                    "placeholder": "Aug 2025 – Present",
                    "maxlength": 100,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Focus areas, activities, results",
                    "rows": 3,
                }
            ),
        }

    def clean_institution(self):
        institution = self.cleaned_data.get("institution", "")
        return strip_tags(institution)

    def clean_degree(self):
        degree = self.cleaned_data.get("degree", "")
        return strip_tags(degree)

    def clean_field_of_study(self):
        field_of_study = self.cleaned_data.get("field_of_study", "")
        return strip_tags(field_of_study)

    def clean_start_year(self):
        start_year = self.cleaned_data.get("start_year", "")
        return strip_tags(str(start_year))

    def clean_end_year(self):
        end_year = self.cleaned_data.get("end_year", "")
        return strip_tags(str(end_year))

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
            "title": "Name",
            "description": "Description",
            "tech_stack": "Systems (comma-separated)",
            "project_url": "Project URL",
            "project_image_url": "Image URL",
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
                    "placeholder": "What it does and why it exists",
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

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        return strip_tags(title)

    def clean_description(self):
        description = self.cleaned_data.get("description", "")
        return strip_tags(description)

    def clean_tech_stack(self):
        tech_stack = self.cleaned_data.get("tech_stack", "")
        return strip_tags(tech_stack)

    def clean_project_url(self):
        project_url = self.cleaned_data.get("project_url", "")
        return strip_tags(project_url)

    def clean_project_image_url(self):
        project_image_url = self.cleaned_data.get("project_image_url", "")
        return strip_tags(project_image_url)


class AwardsForm(ModelForm):
    # The category picks the ribbon's family (where the red goes). Optional, so
    # older forms that never sent it keep working; it falls back to "honor".
    category = forms.ChoiceField(
        choices=[("", "Choose a category")] + Award.AWARD_TYPE_CHOICES,
        required=False,
        label="Category (sets the ribbon)",
    )

    def clean_category(self):
        return self.cleaned_data.get("category") or "honor"

    class Meta:
        model = Award
        fields = [
            "title",
            "issuer",
            "category",
            "date_awarded",
            "description",
        ]

        labels = {
            "title": "Title",
            "issuer": "Issued by",
            "date_awarded": "Date awarded",
            "description": "Citation",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "1st place, national hackathon",
                    "maxlength": 255,
                }
            ),
            "issuer": TextInput(
                attrs={
                    "placeholder": "Organiser",
                    "maxlength": 255,
                }
            ),
            "date_awarded": TextInput(
                attrs={
                    "placeholder": "Aug 2026",
                    "maxlength": 100,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "What it was for, in a sentence or two",
                    "rows": 3,
                }
            ),
        }