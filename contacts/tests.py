from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from .models import ContactMessage

@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"])
class ContactTests(TestCase):
    def test_form_persists_message(self):
        response = self.client.post("/", {"name": "Teste", "email": "test@example.com", "message": "Olá"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.get().message, "Olá")
        self.assertEqual(self.client.get("/healthz").status_code, 200)

    def test_invalid_form_does_not_write(self):
        self.client.post("/", {"name": "Teste", "email": "invalid", "message": "Olá"})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_inbox_requires_staff(self):
        self.assertEqual(self.client.get("/equipe/").status_code, 302)
        user = get_user_model().objects.create_user(username="visitor", password="test-only-password")
        self.client.force_login(user)
        self.assertEqual(self.client.get("/equipe/").status_code, 302)
        user.is_staff = True
        user.save()
        ContactMessage.objects.create(name="Teste", email="test@example.com", message="<script>alert(1)</script>")
        response = self.client.get("/equipe/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
