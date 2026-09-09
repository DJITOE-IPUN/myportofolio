from django.urls import path

from main.views import show_awards, show_education, show_experience, show_main

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path('education/', show_education, name='show_education'),
    path('awards/', show_awards, name='show_awards'),
]