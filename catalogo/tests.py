from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import UnidadMedida
from .services import convertir_a_unidad_base


class UnidadMedidaModelTests(TestCase):
    def test_initial_units_are_created_by_migration(self):
        expected = {"g", "kg", "ml", "L", "und"}

        self.assertTrue(expected.issubset(set(UnidadMedida.objects.values_list("abreviatura", flat=True))))

    def test_derived_unit_must_match_base_type(self):
        gramo = UnidadMedida.objects.get(abreviatura="g")
        with self.assertRaises(ValidationError):
            UnidadMedida(
                nombre="litro invalido",
                abreviatura="li",
                tipo=UnidadMedida.Tipo.VOLUMEN,
                factor_conversion=Decimal("1000"),
                unidad_base=gramo,
            ).full_clean()


class ConversionServiceTests(TestCase):
    def test_convert_weight_to_base_unit(self):
        kilogramo = UnidadMedida.objects.get(abreviatura="kg")

        self.assertEqual(convertir_a_unidad_base(Decimal("2.5"), kilogramo), Decimal("2500.000000"))

    def test_convert_volume_to_base_unit(self):
        litro = UnidadMedida.objects.get(abreviatura="L")

        self.assertEqual(convertir_a_unidad_base("1.5", litro), Decimal("1500.000000"))

    def test_rejects_negative_quantities(self):
        gramo = UnidadMedida.objects.get(abreviatura="g")

        with self.assertRaises(ValueError):
            convertir_a_unidad_base("-1", gramo)


class UnidadMedidaViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@postres.local",
            password="clave-segura-123",
        )

    def grant(self, codename):
        permission = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(permission)

    def test_list_requires_login(self):
        response = self.client.get(reverse("catalogo:unidad_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response["Location"])

    def test_user_with_view_permission_can_list_units(self):
        self.grant("view_unidadmedida")
        self.client.force_login(self.user)

        response = self.client.get(reverse("catalogo:unidad_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "kilogramo")

    def test_user_with_add_permission_can_create_unit(self):
        gramo = UnidadMedida.objects.get(abreviatura="g")
        self.grant("add_unidadmedida")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("catalogo:unidad_create"),
            {
                "nombre": "libra",
                "abreviatura": "lb",
                "tipo": UnidadMedida.Tipo.PESO,
                "factor_conversion": "453.592000",
                "unidad_base": gramo.pk,
                "activo": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(UnidadMedida.objects.filter(abreviatura="lb").exists())

    def test_user_with_change_permission_can_toggle_unit(self):
        gramo = UnidadMedida.objects.get(abreviatura="g")
        self.grant("change_unidadmedida")
        self.client.force_login(self.user)

        response = self.client.post(reverse("catalogo:unidad_toggle_active", args=[gramo.pk]))

        gramo.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(gramo.activo)
