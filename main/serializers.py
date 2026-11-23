from django.utils.html import strip_tags
from rest_framework import serializers

from main.afterburner import YEAR_RE, build_qualifications, parse_period
from main.models import Education, Project


class ProjectSerializer(serializers.ModelSerializer):
    # Computed, read-only fields. The model's relation is called `stars`
    # (the tutorial calls it `starred_by`); the API keeps the tutorial's names.
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.stars.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.stars.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.stars.all())


# ---------------------------------------------------------------------------
# Tugas 6: Education ("Qualifications"), the section built in Tugas 3-5
# ---------------------------------------------------------------------------

def qualification_index(educations):
    """Map every Education id to its Afterburner card data (code, status, progress…).

    The TR-xx codes are numbered over *all* records, newest first, so a card keeps
    its code while the list is being searched. Pass the result to
    EducationSerializer as context["qualifications"].
    """
    return {qual["obj"].pk: qual for qual in build_qualifications(educations)}


class EducationSerializer(serializers.ModelSerializer):
    """One qualification. Writable: the five model fields. Everything else is computed."""

    degree_display = serializers.CharField(source="get_degree_display", read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    qualification = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            "id", "institution", "degree", "degree_display",
            "field_of_study", "date_range", "description",
            "star_count", "is_starred", "qualification",
        ]
        read_only_fields = ["id"]

    # ----- validation: same clean-up as EducationForm.clean_<field> (Tugas 5) -----

    @staticmethod
    def _clean_required(value, label):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError(f"{label} cannot be empty.")
        return value

    def validate_institution(self, value):
        return self._clean_required(value, "Institution")

    def validate_field_of_study(self, value):
        return self._clean_required(value, "Field of study")

    def validate_date_range(self, value):
        value = self._clean_required(value, "Period")
        # The card works out status and semester from this text, so it needs a year.
        if not YEAR_RE.search(value):
            raise serializers.ValidationError("Period needs at least one year, like “Aug 2025 – Present”.")
        return value

    def validate_description(self, value):
        return strip_tags(value or "").strip()

    # ----- computed, read-only fields -----

    def get_star_count(self, obj):
        return len(obj.stars.all())  # uses prefetch_related("stars") when the view set it up

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in obj.stars.all())

    def get_qualification(self, obj):
        qual = self.context.get("qualifications", {}).get(obj.pk)
        if qual is None:  # e.g. a record that was just created
            qual = qualification_index(Education.objects.all()).get(obj.pk)
        if qual is None:
            return None
        period = parse_period(obj.date_range, start_month=8, end_month=6)
        return {
            "code": qual["code"],
            "rating": qual["rating"],
            "status": qual["status"],
            "ongoing": qual["ongoing"],
            "semester": qual["semester"],
            "semesters": qual["semesters"],
            "progress": qual["progress"],
            "start_year": str(period.start.year) if period.start else "",
            "end_year": "Present" if period.ongoing else (str(period.end.year) if period.end else ""),
        }
