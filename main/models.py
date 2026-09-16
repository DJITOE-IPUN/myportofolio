import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Depok, West Java")
    date_range = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default='ORGANIZATION')
    description = models.TextField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.organization}"


class Education(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'S1 / Bachelor Degree'),
        ('secondary_school', 'SMP/SMA / High School'),
        ('diploma', 'Diploma'),
        ('master', 'S2 / Master Degree'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, default='bachelor')
    field_of_study = models.CharField(max_length=255, default="Computer Science")
    date_range = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_degree_display()} - {self.institution}"


class Award(models.Model):
    AWARD_TYPE_CHOICES = [
        ('academic', 'Academic / Scholarship'),
        ('competition', 'Competition / Hackathon'),
        ('leadership', 'Leadership / Organizational'),
        ('honor', 'Honorary Mention'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=AWARD_TYPE_CHOICES, default='competition')
    date_awarded = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.issuer})"

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255)
    project_url = models.URLField(blank=True)
    project_image_url = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.title