from django.shortcuts import render

from main.models import Experience


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