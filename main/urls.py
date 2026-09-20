from django.urls import path
from main.views import (
    show_main, show_education, show_awards, show_projects, show_experience,
    create_education, create_project, create_award,
    edit_education, edit_project, edit_award,
    delete_education, delete_project, delete_award,
    show_json_education, show_json_projects, show_json_awards, show_json_by_id
)

app_name = 'main'

urlpatterns = [
    # Main Views
    path('', show_main, name='show_main'),
    path('experience/', show_experience, name='show_experience'),
    path('education/', show_education, name='show_education'),
    path('awards/', show_awards, name='show_awards'),
    path('projects/', show_projects, name='show_projects'),

    # Create Routes
    path('education/create/', create_education, name='create_education'),
    path('projects/create/', create_project, name='create_project'),
    path('awards/create/', create_award, name='create_award'),

    # Edit Routes
    path('education/edit/<uuid:id>/', edit_education, name='edit_education'),
    path('projects/edit/<uuid:id>/', edit_project, name='edit_project'),
    path('awards/edit/<uuid:id>/', edit_award, name='edit_award'),

    # Delete Routes
    path('education/delete/<uuid:id>/', delete_education, name='delete_education'),
    path('projects/delete/<uuid:id>/', delete_project, name='delete_project'),
    path('awards/delete/<uuid:id>/', delete_award, name='delete_award'),

    # JSON Data Delivery Routes
    path('json/education/', show_json_education, name='show_json_education'),
    path('json/projects/', show_json_projects, name='show_json_projects'),
    path('json/awards/', show_json_awards, name='show_json_awards'),
    path('json/<str:model_type>/<uuid:id>/', show_json_by_id, name='show_json_by_id'),
]