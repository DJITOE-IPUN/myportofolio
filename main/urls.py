from django.urls import path
from main.views import (
    show_main, show_education, show_awards, show_projects, show_experience,
    create_education, create_project, create_award,
    edit_education, edit_project, edit_award,
    delete_education, delete_project, delete_award,
    show_json_education, show_json_projects, show_json_awards, show_json_by_id, 
    register, login_user, logout_user, toggle_star
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
    path('education/edit/<str:id>/', edit_education, name='edit_education'),
    path('projects/edit/<str:id>/', edit_project, name='edit_project'),
    path('awards/edit/<str:id>/', edit_award, name='edit_award'),

    # Delete Routes
    path('education/delete/<str:id>/', delete_education, name='delete_education'),
    path('projects/delete/<str:id>/', delete_project, name='delete_project'),
    path('awards/delete/<str:id>/', delete_award, name='delete_award'),

    # JSON Data Delivery Routes
    path('json/education/', show_json_education, name='show_json_education'),
    path('json/projects/', show_json_projects, name='show_json_projects'),
    path('json/awards/', show_json_awards, name='show_json_awards'),
    path('json/<str:model_type>/<str:id>/', show_json_by_id, name='show_json_by_id'),

    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    
    path('experience/<uuid:id>/star/', toggle_star, name='toggle_star'),
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
]