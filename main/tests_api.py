import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class EducationAPITest(APITestCase):
    """Tugas 6: /api/v1/education/ with the four roles from Tugas 4."""

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password="test-password", email="visitor@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        # The test database is empty, so the Editor group from Tugas 4 is made here
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.education = Education.objects.create(
            institution="Universitas Indonesia", degree="bachelor",
            field_of_study="Ilmu Komputer", date_range="Aug 2025 – Present",
            description="Fasilkom",
        )
        Education.objects.create(
            institution="SMA Taruna", degree="secondary_school",
            field_of_study="MIPA", date_range="2022 – 2025",
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "institution": "Institut Teknologi Bandung", "degree": "master",
            "field_of_study": "Informatika", "date_range": "2029 – 2031",
            "description": "Planned",
        }

    def assertUnchanged(self):
        """The record in the database is exactly as setUp left it."""
        self.assertEqual(Education.objects.count(), 2)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia")
        self.assertEqual(self.education.field_of_study, "Ilmu Komputer")

    # ----- reading -----

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        first = response.data[0]
        self.assertEqual(first["id"], str(self.education.id))  # newest first, like the cards
        self.assertEqual(first["degree_display"], "S1 / Bachelor Degree")
        self.assertEqual(first["qualification"]["code"], "TR-01")
        self.assertEqual(first["qualification"]["status"], "In training")
        self.assertEqual((first["star_count"], first["is_starred"]), (0, False))

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["institution"], "Universitas Indonesia")

    def test_explicit_fields_and_no_account_data(self):
        self.education.stars.add(self.visitor)
        data = self.client.get(self.detail_url).data
        self.assertEqual(set(data), {
            "id", "institution", "degree", "degree_display", "field_of_study",
            "date_range", "description", "star_count", "is_starred", "qualification",
        })
        self.assertNotIn("visitor@example.com", str(data))
        self.assertNotIn("pbkdf2", str(data))

    def test_search_by_institution_query_param(self):
        response = self.client.get(self.list_url, {"institution": "taruna"})
        self.assertEqual([e["institution"] for e in response.data], ["SMA Taruna"])
        # the TR code is numbered over every record, so it doesn't change while searching
        self.assertEqual(response.data[0]["qualification"]["code"], "TR-02")
        self.assertEqual(self.client.get(self.list_url, {"institution": "nothing"}).data, [])

    def test_missing_record_is_404(self):
        url = reverse("api:education-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.patch(url, {"institution": "X"}, format="json").status_code, 404)
        star = reverse("api:education-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(star).status_code, status.HTTP_404_NOT_FOUND)

    # ----- the four roles -----

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"institution": "Hacked"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertUnchanged()
        self.assertFalse(Education.objects.filter(institution="Institut Teknologi Bandung").exists())

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"field_of_study": "Sistem Informasi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.field_of_study, "Sistem Informasi")
        self.assertEqual(self.education.institution, "Universitas Indonesia")  # PATCH left it alone

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Institut Teknologi Bandung")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertUnchanged()
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())

    def test_staff_without_editor_group_cannot_write(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {"institution": "Hacked"}, format="json").status_code, 403)
        self.assertUnchanged()

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Education.objects.filter(pk=response.data["id"]).exists())
        self.assertEqual(response.data["qualification"]["rating"], "S2")

        response = self.client.patch(self.detail_url, {"description": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())

    def test_put_needs_every_required_field(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"institution": "Only this"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("field_of_study", response.data)
        self.assertUnchanged()

    # ----- validation (validate_<field>) -----

    def test_validation_rejects_bad_input(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution": "   "}, "institution"),
            ({"institution": '<img src="x" onerror="alert(1)">'}, "institution"),  # nothing left after strip_tags
            ({"field_of_study": "<b></b>"}, "field_of_study"),
            ({"date_range": "sometime soon"}, "date_range"),
            ({"degree": "phd"}, "degree"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, changes)
            self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 2)

    def test_validation_strips_tags(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            "institution": "<b>ITB</b>",
            "description": '<img src="x" onerror="alert(1)">Bandung',
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Education.objects.get(pk=response.data["id"])
        self.assertEqual(created.institution, "ITB")
        self.assertEqual(created.description, "Bandung")

    def test_editor_patch_is_validated_too(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"date_range": "<i>soon</i>"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_range", response.data)
        self.education.refresh_from_db()
        self.assertEqual(self.education.date_range, "Aug 2025 – Present")

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "stars": [self.visitor.id], "qualification": {"code": "TR-99"},
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(Education.objects.get(pk=response.data["id"]).stars.count(), 0)

    # ----- star -----

    def test_star_rejects_guests(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.education.stars.count(), 0)

    def test_star_toggles_for_the_signed_in_account(self):
        self.client.force_authenticate(user=self.visitor)
        # whatever the body says, the star belongs to request.user
        response = self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data["star_count"], response.data["is_starred"]), (1, True))
        self.assertEqual(list(self.education.stars.all()), [self.visitor])

        response = self.client.post(self.star_url)
        self.assertEqual((response.data["star_count"], response.data["is_starred"]), (0, False))
        self.assertEqual(self.education.stars.count(), 0)

    def test_every_role_can_star(self):
        for user in (self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.education.stars.count(), 3)
        self.client.force_authenticate(user=self.editor)
        self.assertTrue(self.client.get(self.detail_url).data["is_starred"])

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----- CSRF with a real session login -----

    def test_session_writes_without_csrf_are_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(client.patch(self.detail_url, {"institution": "Forged"}, format="json").status_code, 403)
        self.assertEqual(client.delete(self.detail_url).status_code, 403)
        self.assertUnchanged()

        visitor = APIClient(enforce_csrf_checks=True)
        self.assertTrue(visitor.login(username="visitor", password="test-password"))
        self.assertEqual(visitor.post(self.star_url).status_code, 403)
        self.assertEqual(self.education.stars.count(), 0)

    def test_session_write_with_csrf_token_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="editor", password="test-password")
        # The Education page sets the csrftoken cookie for every role (@ensure_csrf_cookie)
        page = client.get(reverse("main:show_education"))
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.patch(
            self.detail_url, {"field_of_study": "Sistem Informasi"}, format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_browsable_api_renders(self):
        response = self.client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Education List")
