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
    
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Depok, West Java")
    date_range = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default='ORGANIZATION')
    description = models.TextField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.organization}"
