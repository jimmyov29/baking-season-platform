from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


class UsuarioModelTests(TestCase):
    def test_create_user_normalizes_email_and_blank_phone(self):
        user = get_user_model().objects.create_user(
            email="ADMIN@POSTRES.LOCAL",
            password="clave-segura-123",
            telefono="",
        )

        self.assertEqual(user.email, "admin@postres.local")
        self.assertIsNone(user.telefono)
        self.assertTrue(user.check_password("clave-segura-123"))
        self.assertFalse(user.is_staff)

    def test_create_superuser_requires_staff_and_superuser_flags(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email="admin@postres.local",
                password="clave-segura-123",
                is_staff=False,
            )


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="ventas@postres.local",
            telefono="99990000",
            password="clave-segura-123",
            first_name="Ventas",
            last_name="Postres",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response["Location"])

    def test_user_can_login_with_email(self):
        response = self.client.post(
            reverse("usuarios:login"),
            {"username": "ventas@postres.local", "password": "clave-segura-123"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:home"))

    def test_user_can_login_with_phone(self):
        response = self.client.post(
            reverse("usuarios:login"),
            {"username": "99990000", "password": "clave-segura-123"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:home"))

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            reverse("usuarios:login"),
            {"username": "ventas@postres.local", "password": "clave-segura-123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Por favor", status_code=200)

    def test_authenticated_user_can_access_home(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ventas Postres")


class PasswordFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@postres.local",
            password="clave-segura-123",
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_sends_email(self):
        response = self.client.post(
            reverse("usuarios:password_reset"),
            {"email": "admin@postres.local"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_change_requires_login(self):
        response = self.client.get(reverse("usuarios:password_change"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response["Location"])


class InitialGroupsTests(TestCase):
    def test_initial_roles_exist(self):
        expected_groups = {"ADMINISTRADOR", "VENTAS", "COMPRAS", "PRODUCCION", "SOCIO"}

        self.assertTrue(expected_groups.issubset(set(Group.objects.values_list("name", flat=True))))
