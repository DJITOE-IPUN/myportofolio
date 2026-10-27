from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from main.models import Education, Project, Award, Experience
from main.forms import EducationForm, ProjectForm, AwardsForm
from main.telemetry import get_github_telemetry
from main.afterburner import (
    build_sorties, sortie_stats, flight_path, build_qualifications, build_rack, parse_period,
)
from main.coolwall import COOL_WALL, COOL_WALL_ZONES
from main.telemetry import get_github_telemetry

import datetime

NAME = 'Michael Evan Putra Nugroho'

def check_is_editor(user):
    return user.is_authenticated and (user.groups.filter(name='Editor').exists() or user.is_superuser)

# --- VIEWS UTAMA ---
def collect_stack(projects):
    """Unique tech-stack items across all projects, in first-seen order (for the homepage marquee)."""
    seen = {}
    for project in projects:
        for item in (project.tech_stack or "").split(","):
            item = item.strip()
            if item and item.lower() not in seen:
                seen[item.lower()] = item
    return list(seen.values())


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'No sign-in yet')
    project_list = Project.objects.all()
    project_list = Project.objects.all()
    context = {
        'name': NAME,
        'npm': '2506616674',
        'study_program': 'S1 Ilmu Komputer',
        'bio': (
            "Hi, I'm Evan. Computer Science student at Universitas Indonesia driven by a passion for defence tech & system engineering."
        ),
        "last_login": last_login,
        # Afterburner: radar counts and the one-page CV shown in Unclassified mode
        'experience_list': Experience.objects.all(),
        'education_list': Education.objects.all(),
        'award_list': Award.objects.all(),
        'project_list': project_list,
        'stack_list': collect_stack(project_list),
        # Afterburner: GitHub telemetry for the display (None without GITHUB_TOKEN)
        'telemetry': get_github_telemetry(),
    }
    return render(request, "index.html", context)

def show_experience(request):
    # Afterburner "Sorties": experiences in flight order with derived debrief data
    sorties = build_sorties(Experience.objects.prefetch_related('stars'), user=request.user)
    context = {
        'name': NAME,
        'experience_list': [sortie['obj'] for sortie in sorties],
        'sorties': sorties,
        'stats': sortie_stats(sorties),
        'path': flight_path(len(sorties)),
    }
    return render(request, "experience.html", context)

def show_education(request):
    # Afterburner "Qualifications". The cards are rendered here first (so the page
    # works without JavaScript), then qualifications.js keeps them live over AJAX:
    # show_json_education for the list and search, create_education_ajax for adding.
    title_query = request.GET.get('title', '')
    qualifications = build_qualifications(Education.objects.all())
    context = {
        'name': NAME,
        'form': EducationForm(),
        'title': title_query,
        'is_editor': check_is_editor(request.user),
        'education_list': [qual['obj'] for qual in qualifications],
        'qualifications': qualifications,
        'in_training': sum(1 for qual in qualifications if qual['ongoing']),
    }
    return render(request, "education.html", context)

def show_awards(request):
    # Afterburner "Ribbon rack": one generated ribbon per award
    citations, rack = build_rack(Award.objects.all())
    context = {
        'name': NAME,
        'award_list': [item['obj'] for item in citations],
        'citations': citations,
        'rack': rack,
        'is_editor': check_is_editor(request.user),
    }
    return render(request, "awards.html", context)

def show_coolwall(request):
    # Easter egg: the Cool Wall (verdicts live in main/coolwall.py)
    context = {
        'name': NAME,
        'zones': [
            {**zone, 'items': [item for item in COOL_WALL if item['zone'] == zone['key']]}
            for zone in COOL_WALL_ZONES
        ],
        'item_count': len(COOL_WALL),
    }
    return render(request, "coolwall.html", context)

def show_projects(request):
    title_query = request.GET.get('title', '')
    context = {
        'name': NAME,
        'project_count': Project.objects.count(),
        'title_query': title_query,
        'is_editor': check_is_editor(request.user),
        "form": ProjectForm(),
    }
    return render(request, "projects.html", context)


# --- CREATE VIEWS ---
@login_required(login_url='main:login')
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied  # themed templates/403.html
    form = EducationForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_education')
    return render(request, "education_form.html", {'form': form, 'title': 'Add qualification', 'code': 'TR-NEW'})

@login_required(login_url='main:login')
@require_POST
def create_education_ajax(request):
    # Otorisasi ketat di sisi server
    if not request.user.is_superuser:
        return JsonResponse({
            'error': 'Only the owner of this portfolio can add records.'
        }, status=403)

    form = EducationForm(request.POST)
    if form.is_valid():
        edu = form.save()
        return JsonResponse({
            'message': f'{edu.institution} added to the record.',
            'id': str(edu.id)
        }, status=201)
    else:
        return JsonResponse({
            'error': 'Some fields need another look.',
            'errors': form.errors
        }, status=400)

@login_required(login_url='main:login')
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied  # themed templates/403.html
    form = ProjectForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_projects')
    return render(request, "projects_form.html", {'form': form, 'title': 'Commission airframe', 'code': 'AF-NEW'})

@login_required(login_url='main:login')
@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse({
            'error': 'Only the owner of this portfolio can commission airframes.'
        }, status=403)

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse({
            'message': f'{project.title} commissioned. It is in the hangar.',
            'id': str(project.id)
        }, status=201)
    else:
        return JsonResponse({
            'error': 'Some fields need another look.',
            'errors': form.errors
        }, status=400)

@login_required(login_url='main:login')
def create_award(request):
    if not request.user.is_superuser:
        raise PermissionDenied  # themed templates/403.html
    form = AwardsForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_awards')
    return render(request, "awards_form.html", {'form': form, 'title': 'Add citation', 'code': 'CIT-NEW'})


# --- EDIT / UPDATE VIEWS ---
@login_required(login_url='main:login')
def edit_education(request, id):
    if not check_is_editor(request.user):
        raise PermissionDenied  # themed templates/403.html
    edu = get_object_or_404(Education, pk=id)
    form = EducationForm(request.POST or None, instance=edu)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_education')
    return render(request, "education_form.html", {'form': form, 'title': 'Edit qualification', 'code': 'TR-EDIT', 'record': edu})

@login_required(login_url='main:login')
def edit_project(request, id):
    if not check_is_editor(request.user):
        raise PermissionDenied  # themed templates/403.html
    project = get_object_or_404(Project, pk=id)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_projects')
    return render(request, "projects_form.html", {'form': form, 'title': 'Refit airframe', 'code': 'AF-EDIT', 'record': project})

@login_required(login_url='main:login')
def edit_award(request, id):
    if not check_is_editor(request.user):
        raise PermissionDenied  # themed templates/403.html
    award = get_object_or_404(Award, pk=id)
    form = AwardsForm(request.POST or None, instance=award)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_awards')
    return render(request, "awards_form.html", {'form': form, 'title': 'Edit citation', 'code': 'CIT-EDIT', 'record': award})


# --- DELETE VIEWS ---
@login_required(login_url='main:login')
@require_POST
def delete_education(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied  # themed templates/403.html
    if request.method == "POST":
        edu = get_object_or_404(Education, pk=id)
        edu.delete()
    return redirect('main:show_education')

@login_required(login_url='main:login')
@require_POST
def delete_project(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied  # themed templates/403.html
    if request.method == "POST":
        project = get_object_or_404(Project, pk=id)
        project.delete()
    return redirect('main:show_projects')

@login_required(login_url='main:login')
@require_POST
def delete_award(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied  # themed templates/403.html
    if request.method == "POST":
        award = get_object_or_404(Award, pk=id)
        award.delete()
    return redirect('main:show_awards')


# --- JSON DATA DELIVERY ENDPOINTS ---
def show_json_education(request):
    query = request.GET.get('institution', '').strip()

    if query:
        educations = Education.objects.filter(institution__icontains=query)
    else:
        educations = Education.objects.all()

    # Education stores one free-text `date_range` ("2025 – Present"), so the
    # start/end years are read from it. The qualification fields (status,
    # semester, progress…) feed the Afterburner cards in qualifications.js.
    education_list = []
    for qual in build_qualifications(educations):
        edu = qual['obj']
        period = parse_period(edu.date_range, start_month=8, end_month=6)
        education_list.append({
            'id': str(edu.id),
            'institution': edu.institution,
            'degree': edu.get_degree_display(),
            'degree_key': edu.degree,
            'field_of_study': edu.field_of_study,
            'date_range': edu.date_range,
            'start_year': str(period.start.year) if period.start else '',
            'end_year': 'Present' if period.ongoing else (str(period.end.year) if period.end else ''),
            'description': edu.description or '',
            'code': qual['code'],
            'rating': qual['rating'],
            'status': qual['status'],
            'ongoing': qual['ongoing'],
            'semester': qual['semester'],
            'semesters': qual['semesters'],
            'progress': qual['progress'],
            # Education has no stars field; kept for a consistent JSON shape
            'total_stars': 0,
            'is_starred': False,
        })

    return JsonResponse({
        'educations': education_list,
        'user_permissions': {
            'is_authenticated': request.user.is_authenticated,
            'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
            'is_editor': check_is_editor(request.user),
        }
    }, status=200)

def show_json_projects(request):
    title_query = request.GET.get('title', '').strip()
    
    if title_query:
        projects = Project.objects.filter(title__icontains=title_query)
    else:
        projects = Project.objects.all()

    project_list = []
    for p in projects:
        # Cek apakah user saat ini memberi star pada project ini
        is_starred = p.stars.filter(id=request.user.id).exists() if request.user.is_authenticated else False
        
        project_list.append({
            'id': str(p.id),
            'title': p.title,
            'description': p.description,
            'tech_stack': p.tech_stack,
            'project_url': p.project_url or '',
            'project_image_url': p.project_image_url or '',
            'total_stars': p.stars.count(),
            'is_starred': is_starred,
        })

    return JsonResponse({
        'projects': project_list,
        'user_permissions': {
            'is_authenticated': request.user.is_authenticated,
            'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
            'is_editor': check_is_editor(request.user),
        }
    }, status=200)

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

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created. Sign in to continue.")
        return redirect("main:login")

    context = {
        "name": NAME,
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": NAME,
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response


# --- TOGGLE STAR (Logged-in User) ---
# One view serves both star routes; the route name decides which model is starred.
STAR_TARGETS = {
    'toggle_experience_star': (Experience, 'main:show_experience'),
    'toggle_project_star': (Project, 'main:show_projects'),
}

def wants_json(request):
    return (request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or 'application/json' in request.headers.get('accept', ''))

@login_required(login_url='main:login')
@require_POST
def toggle_star(request, id):
    model, list_view = STAR_TARGETS.get(
        getattr(request.resolver_match, 'url_name', ''), STAR_TARGETS['toggle_project_star']
    )
    obj = get_object_or_404(model, pk=id)
    starred = not obj.stars.filter(id=request.user.id).exists()
    if starred:
        obj.stars.add(request.user)
    else:
        obj.stars.remove(request.user)

    if wants_json(request):
        return JsonResponse({'starred': starred, 'count': obj.stars.count()})
    return redirect(list_view)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('stars').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.stars.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)