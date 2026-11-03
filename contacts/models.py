from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    # Tutorial 06, latihan 1
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name
