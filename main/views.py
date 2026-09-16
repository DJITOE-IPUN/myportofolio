from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Award, Education, Experience, Project
from main.forms import *


def show_main(request):
    context = {
        "name": "Michael Evan Putra Nugroho",
        "npm": "2506616674",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Hi, I'm Evan. "
            "A Computer Science student driven by a strong curiosity about military and aviation technology, and how innovation can shape the future of defence and security. "
            "I am committed to combining my expertise in programming and system analysis with my passion for defence and security innovation to create technology solutions that make a real impact."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Michael Evan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_education(request):
    education_list = Education.objects.all()
    context = {
        'name': 'Michael Evan',
        'education_list': education_list,
    }
    return render(request, "education.html", context)


def show_awards(request):
    award_list = Award.objects.all()
    context = {
        'name': 'Michael Evan',
        'award_list': award_list,
    }
    return render(request, "awards.html", context)

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Michael Evan",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "projects.html", context)

# def add_education(request):
#     form = EducationForm(request.POST or None)

#     if request.method == "POST" and form.is_valid():
#         form.save()
#         messages.success(request, "Institusi pendidikan berhasil ditambahkan!")
#         return redirect("main:show_projects")

#     context = {
#         "name": "Michael Evan",
#         "form": form,
#     }
#     return render(request, "education_form.html", context)

def add_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")