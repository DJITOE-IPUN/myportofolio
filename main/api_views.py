from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import EducationSerializer, ProjectSerializer, qualification_index

# Tutorial 10: every API view accepts a token (the Flutter app) and the session
# cookie (the website and the Browsable API). Same order as
# REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]: Token first, so a missing or
# revoked token is answered with 401 instead of 403.
API_AUTHENTICATION = [TokenAuthentication, SessionAuthentication]


@api_view(["GET", "HEAD", "POST"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("stars").order_by("title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("stars"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.stars.filter(pk=request.user.pk).exists():
        project.stars.remove(request.user)
    else:
        project.stars.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# Tugas 6: Education ("Qualifications")
#   GET    /api/v1/education/?institution=…   everyone (search moved here from Tugas 5)
#   POST   /api/v1/education/                 owner only                -> 201 / 400 / 403
#   GET    /api/v1/education/<id>/            everyone                  -> 200 / 404
#   PUT    /api/v1/education/<id>/            Editor and owner          -> 200 / 400 / 403
#   PATCH  /api/v1/education/<id>/            Editor and owner          -> 200 / 400 / 403
#   DELETE /api/v1/education/<id>/            owner only                -> 204 / 403
#   POST   /api/v1/education/<id>/star/       any logged-in account     -> 200 / 403
# Who may do what lives in IsPortfolioOwnerOrEditorOrReadOnly; validation lives
# in EducationSerializer. The views only route requests to them.
# ---------------------------------------------------------------------------

def education_queryset():
    return Education.objects.prefetch_related("stars")


def education_context(request):
    """Serializer context with fresh card data (TR codes, status, progress) for every record."""
    return {"request": request, "qualifications": qualification_index(Education.objects.all())}


def education_response(request, education, status_code=status.HTTP_200_OK):
    """Serialize one record after a write, so star and card data are up to date."""
    education = education_queryset().get(pk=education.pk)
    serializer = EducationSerializer(education, context=education_context(request))
    return Response(serializer.data, status=status_code)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    if request.method in ("GET", "HEAD"):
        context = education_context(request)
        educations = education_queryset()
        institution = request.query_params.get("institution", "").strip()
        if institution:
            educations = educations.filter(institution__icontains=institution)
        # Same order as the cards: newest first (the order of the TR codes)
        order = {pk: qual["index"] for pk, qual in context["qualifications"].items()}
        educations = sorted(educations, key=lambda edu: order.get(edu.pk, 0))
        serializer = EducationSerializer(educations, many=True, context=context)
        return Response(serializer.data)

    serializer = EducationSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    education = serializer.save()
    return education_response(request, education, status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    education = get_object_or_404(education_queryset(), pk=education_id)
    if request.method in ("GET", "HEAD"):
        serializer = EducationSerializer(education, context=education_context(request))
        return Response(serializer.data)

    if request.method == "DELETE":
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = EducationSerializer(
        education, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return education_response(request, education)


@api_view(["POST"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    """Toggle the signed-in account's star. The account always comes from request.user."""
    education = get_object_or_404(Education, pk=education_id)
    if education.stars.filter(pk=request.user.pk).exists():
        education.stars.remove(request.user)
    else:
        education.stars.add(request.user)
    return education_response(request, education)


# ---------------------------------------------------------------------------
# Tutorial 10: token login and logout for the Flutter app
#   POST /api/v1/auth/token/    username + password -> {"token": "..."}  (DRF's obtain_auth_token)
#   POST /api/v1/auth/logout/   Authorization: Token <key>  -> 204, the token is deleted
# ---------------------------------------------------------------------------

@api_view(["POST"])
@authentication_classes(API_AUTHENTICATION)
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Revoke the caller's token. A session login has no token, so nothing is deleted."""
    if request.auth is not None:
        request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
