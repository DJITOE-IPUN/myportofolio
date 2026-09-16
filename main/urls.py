from django.urls import path

from main.views import show_awards, show_education, show_experience, show_main, show_projects, add_education, add_project, delete_project, get_projects_json

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path('education/', show_education, name='show_education'),
    path('awards/', show_awards, name='show_awards'),
    path("projects/", show_projects, name="show_projects"),
    # path("education/add/", add_education, name="add_education"),
    path("projects/add/", add_project, name="add_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
]