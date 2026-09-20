from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from main.models import Education, Project, Award, Experience
from main.forms import EducationForm, ProjectForm, AwardsForm

# --- VIEWS UTAMA ---
def show_main(request):
    context = {
        'name': 'Michael Evan Putra Nugroho',
        'npm': '2506616674',
        'study_program': 'S1 Ilmu Komputer',
        'bio': "Hi, I'm Evan. Computer Science student at Universitas Indonesia driven by a passion for defence tech & system engineering.",
    }
    return render(request, "index.html", context)

def show_experience(request):
    experience_list = Experience.objects.all()
    context = {
        'name': 'Michael Evan Putra Nugroho',
        'experience_list': experience_list,
    }
    return render(request, "experience.html", context)

def show_education(request):
    education_list = Education.objects.all()
    context = {
        'name': 'Michael Evan Putra Nugroho',
        'education_list': education_list,
    }
    return render(request, "education.html", context)

def show_awards(request):
    award_list = Award.objects.all()
    context = {
        'name': 'Michael Evan Putra Nugroho',
        'award_list': award_list,
    }
    return render(request, "awards.html", context)

def show_projects(request):
    title_query = request.GET.get('title', '')
    if title_query:
        project_list = Project.objects.filter(title__icontains=title_query)
    else:
        project_list = Project.objects.all()
        
    context = {
        'name': 'Michael Evan Putra Nugroho',
        'project_list': project_list,
        'title_query': title_query,
    }
    return render(request, "projects.html", context)


# --- CREATE VIEWS ---
def create_education(request):
    form = EducationForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_education')
    return render(request, "education_form.html", {'form': form, 'title': 'Tambah Riwayat Pendidikan'})

def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_projects')
    return render(request, "projects_form.html", {'form': form, 'title': 'Tambah Proyek'})

def create_award(request):
    form = AwardsForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_awards')
    return render(request, "awards_form.html", {'form': form, 'title': 'Tambah Penghargaan'})


# --- EDIT / UPDATE VIEWS ---
def edit_education(request, id):
    edu = get_object_or_404(Education, pk=id)
    form = EducationForm(request.POST or None, instance=edu)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_education')
    return render(request, "education_form.html", {'form': form, 'title': 'Ubah Riwayat Pendidikan'})

def edit_project(request, id):
    project = get_object_or_404(Project, pk=id)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_projects')
    return render(request, "projects_form.html", {'form': form, 'title': 'Ubah Proyek'})

def edit_award(request, id):
    award = get_object_or_404(Award, pk=id)
    form = AwardsForm(request.POST or None, instance=award)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_awards')
    return render(request, "awards_form.html", {'form': form, 'title': 'Ubah Penghargaan'})


# --- DELETE VIEWS ---
def delete_education(request, id):
    if request.method == "POST":
        edu = get_object_or_404(Education, pk=id)
        edu.delete()
    return redirect('main:show_education')

def delete_project(request, id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=id)
        project.delete()
    return redirect('main:show_projects')

def delete_award(request, id):
    if request.method == "POST":
        award = get_object_or_404(Award, pk=id)
        award.delete()
    return redirect('main:show_awards')


# --- JSON DATA DELIVERY ENDPOINTS ---
def show_json_education(request):
    data = Education.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_json_projects(request):
    data = Project.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_json_awards(request):
    data = Award.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_json_by_id(request, model_type, id):
    model_map = {
        'education': Education,
        'project': Project,
        'award': Award,
        'experience': Experience,
    }
    model = model_map.get(model_type.lower())
    if model:
        data = model.objects.filter(pk=id)
        return HttpResponse(serializers.serialize("json", data), content_type="application/json")
    return JsonResponse({'error': 'Model not found'}, status=404)