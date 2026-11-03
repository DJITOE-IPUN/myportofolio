from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact


class ContactHTMXTest(TestCase):
    """Tutorial 06: every HTMX view answers with a fragment, never a full page."""

    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="test-password")
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.ani = Contact.objects.create(name="Ani", email="ani@example.com")
        self.budi = Contact.objects.create(name="Budi", email="budi@example.com", phone="0812")

    def login_owner(self):
        self.client.force_login(self.owner)

    def test_page_is_owner_only(self):
        url = reverse("contacts:contact_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("main:login"), response["Location"])
        self.client.force_login(self.visitor)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(reverse("contacts:contact_add"), {"name": "X", "email": "x@example.com"}).status_code, 403)
        self.assertEqual(Contact.objects.count(), 2)

    def test_anonymous_htmx_request_gets_403(self):
        response = self.client.delete(reverse("contacts:contact_delete", args=[self.ani.pk]), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Contact.objects.filter(pk=self.ani.pk).exists())

    def test_list_page_loads_htmx_and_rows(self):
        self.login_owner()
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "htmx.min.js")
        self.assertContains(response, 'id="contact-rows"')
        self.assertContains(response, f'id="contact-{self.ani.pk}"')

    def test_add_returns_only_the_new_row_and_oob_feedback(self):
        self.login_owner()
        response = self.client.post(reverse("contacts:contact_add"), {"name": "Citra", "email": "citra@example.com", "phone": "021"})
        self.assertEqual(response.status_code, 200)
        citra = Contact.objects.get(name="Citra")
        self.assertContains(response, f'id="contact-{citra.pk}"')
        self.assertNotContains(response, f'id="contact-{self.ani.pk}"')
        self.assertContains(response, 'hx-swap-oob="true"')
        self.assertContains(response, "Contact added.")
        self.assertNotContains(response, "<html")

    def test_add_invalid_swaps_nothing(self):
        self.login_owner()
        response = self.client.post(reverse("contacts:contact_add"), {"name": "", "email": "not-an-email"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Reswap"], "none")
        self.assertContains(response, 'id="feedback"')
        self.assertEqual(Contact.objects.count(), 2)

    def test_search(self):
        self.login_owner()
        response = self.client.get(reverse("contacts:contact_search"), {"q": "AN"})
        self.assertContains(response, "Ani")
        self.assertNotContains(response, "Budi")
        response = self.client.get(reverse("contacts:contact_search"), {"q": "zzz"})
        self.assertContains(response, "No contacts.")

    def test_delete_returns_empty_200(self):
        self.login_owner()
        response = self.client.delete(reverse("contacts:contact_delete", args=[self.ani.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(Contact.objects.filter(pk=self.ani.pk).exists())
        self.assertEqual(self.client.post(reverse("contacts:contact_delete", args=[self.budi.pk])).status_code, 405)

    def test_edit_cancel_and_update(self):
        self.login_owner()
        edit = self.client.get(reverse("contacts:contact_edit", args=[self.budi.pk]))
        self.assertContains(edit, f'form="edit-form-{self.budi.pk}"')
        self.assertContains(edit, 'value="0812"')
        row = self.client.get(reverse("contacts:contact_row", args=[self.budi.pk]))
        self.assertContains(row, "budi@example.com")
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.budi.pk]),
            "name=Budi+S&email=budi.s%40example.com&phone=0899",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "edit-form")
        self.budi.refresh_from_db()
        self.assertEqual((self.budi.name, self.budi.email, self.budi.phone), ("Budi S", "budi.s@example.com", "0899"))

    def test_invalid_update_keeps_edit_row(self):
        self.login_owner()
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.ani.pk]),
            "name=Ani&email=broken",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertContains(response, "edit-form")
        self.assertContains(response, "ab-field-error")
        self.ani.refresh_from_db()
        self.assertEqual(self.ani.email, "ani@example.com")
