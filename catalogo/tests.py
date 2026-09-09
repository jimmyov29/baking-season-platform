from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import CategoriaInsumo, Insumo, UnidadMedida
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



class InsumoModelTests(TestCase):
    def test_initial_categories_are_created_by_migration(self):
        expected = {"Ingrediente", "Empaque", "Decoracion", "Otro"}

        self.assertTrue(expected.issubset(set(CategoriaInsumo.objects.values_list("nombre", flat=True))))

    def test_insumo_requires_base_unit(self):
        categoria = CategoriaInsumo.objects.get(nombre="Ingrediente")
        kilogramo = UnidadMedida.objects.get(abreviatura="kg")

        with self.assertRaises(ValidationError):
            Insumo(
                nombre="Harina invalida",
                categoria=categoria,
                unidad_base=kilogramo,
                stock_minimo=Decimal("0"),
            ).full_clean()

    def test_stock_minimo_cannot_be_negative(self):
        categoria = CategoriaInsumo.objects.get(nombre="Ingrediente")
        gramo = UnidadMedida.objects.get(abreviatura="g")

        with self.assertRaises(ValidationError):
            Insumo(
                nombre="Azucar invalida",
                categoria=categoria,
                unidad_base=gramo,
                stock_minimo=Decimal("-1"),
            ).full_clean()


class InsumoViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="catalogo@postres.local",
            password="clave-segura-123",
        )
        self.categoria = CategoriaInsumo.objects.get(nombre="Ingrediente")
        self.gramo = UnidadMedida.objects.get(abreviatura="g")
        self.insumo = Insumo.objects.create(
            nombre="Harina",
            categoria=self.categoria,
            unidad_base=self.gramo,
            stock_minimo=Decimal("1000"),
        )

    def grant(self, codename):
        permission = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(permission)

    def test_list_requires_login(self):
        response = self.client.get(reverse("catalogo:insumo_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response["Location"])

    def test_user_with_view_permission_can_list_insumos(self):
        self.grant("view_insumo")
        self.client.force_login(self.user)

        response = self.client.get(reverse("catalogo:insumo_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harina")

    def test_user_with_add_permission_can_create_insumo(self):
        self.grant("add_insumo")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("catalogo:insumo_create"),
            {
                "nombre": "Azucar",
                "categoria": self.categoria.pk,
                "unidad_base": self.gramo.pk,
                "stock_minimo": "500.000",
                "activo": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Insumo.objects.filter(nombre="Azucar").exists())

    def test_user_with_change_permission_can_toggle_insumo(self):
        self.grant("change_insumo")
        self.client.force_login(self.user)

        response = self.client.post(reverse("catalogo:insumo_toggle_active", args=[self.insumo.pk]))

        self.insumo.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.insumo.activo)
