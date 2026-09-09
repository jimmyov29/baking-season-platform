from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import CategoriaInsumo, Insumo, Producto, ProductoInsumo, UnidadMedida
from .services import calcular_requerimientos_producto, convertir_a_unidad_base


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



class ProductoRecipeModelTests(TestCase):
    def setUp(self):
        self.categoria = CategoriaInsumo.objects.get(nombre="Ingrediente")
        self.gramo = UnidadMedida.objects.get(abreviatura="g")
        self.kilogramo = UnidadMedida.objects.get(abreviatura="kg")
        self.mililitro = UnidadMedida.objects.get(abreviatura="ml")
        self.harina = Insumo.objects.create(
            nombre="Harina",
            categoria=self.categoria,
            unidad_base=self.gramo,
            stock_minimo=Decimal("1000"),
        )
        self.producto = Producto.objects.create(
            nombre="Brownie",
            descripcion="Brownie clasico",
            precio_venta=Decimal("80.00"),
            rendimiento=12,
        )

    def test_recipe_line_converts_quantity_to_base_unit(self):
        receta = ProductoInsumo.objects.create(
            producto=self.producto,
            insumo=self.harina,
            cantidad=Decimal("0.5"),
            unidad=self.kilogramo,
        )

        self.assertEqual(receta.cantidad_base, Decimal("500.000000"))
        self.assertEqual(receta.cantidad_por_unidad, Decimal("41.66666666666666666666666667"))

    def test_recipe_line_rejects_incompatible_unit(self):
        with self.assertRaises(ValidationError):
            ProductoInsumo(
                producto=self.producto,
                insumo=self.harina,
                cantidad=Decimal("10"),
                unidad=self.mililitro,
            ).full_clean()

    def test_product_rejects_invalid_rendimiento(self):
        with self.assertRaises(ValidationError):
            Producto(nombre="Producto invalido", precio_venta=Decimal("1"), rendimiento=0).full_clean()

    def test_requerimientos_producto_scales_recipe(self):
        ProductoInsumo.objects.create(
            producto=self.producto,
            insumo=self.harina,
            cantidad=Decimal("500"),
            unidad=self.gramo,
        )

        requerimientos = calcular_requerimientos_producto(self.producto, 24)

        self.assertEqual(requerimientos[0]["cantidad_base"], Decimal("1000.000"))


class ProductoViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="productos@postres.local",
            password="clave-segura-123",
        )
        self.categoria = CategoriaInsumo.objects.get(nombre="Ingrediente")
        self.gramo = UnidadMedida.objects.get(abreviatura="g")
        self.harina = Insumo.objects.create(
            nombre="Harina",
            categoria=self.categoria,
            unidad_base=self.gramo,
            stock_minimo=Decimal("1000"),
        )

    def grant(self, *codenames):
        permissions = Permission.objects.filter(codename__in=codenames)
        self.user.user_permissions.add(*permissions)

    def test_list_requires_login(self):
        response = self.client.get(reverse("catalogo:producto_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response["Location"])

    def test_user_with_view_permission_can_list_products(self):
        Producto.objects.create(nombre="Brownie", precio_venta=Decimal("80.00"), rendimiento=12)
        self.grant("view_producto")
        self.client.force_login(self.user)

        response = self.client.get(reverse("catalogo:producto_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brownie")

    def test_user_with_add_permissions_can_create_product_with_recipe(self):
        self.grant("add_producto", "add_productoinsumo")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("catalogo:producto_create"),
            {
                "nombre": "Brownie",
                "descripcion": "Brownie clasico",
                "precio_venta": "80.00",
                "rendimiento": "12",
                "activo": "on",
                "receta-TOTAL_FORMS": "1",
                "receta-INITIAL_FORMS": "0",
                "receta-MIN_NUM_FORMS": "1",
                "receta-MAX_NUM_FORMS": "1000",
                "receta-0-insumo": self.harina.pk,
                "receta-0-cantidad": "500.000",
                "receta-0-unidad": self.gramo.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        producto = Producto.objects.get(nombre="Brownie")
        self.assertEqual(producto.insumos_receta.count(), 1)
        self.assertEqual(producto.insumos_receta.first().cantidad_base, Decimal("500.000000"))

    def test_duplicate_insumo_in_recipe_is_rejected(self):
        self.grant("add_producto", "add_productoinsumo")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("catalogo:producto_create"),
            {
                "nombre": "Brownie",
                "descripcion": "",
                "precio_venta": "80.00",
                "rendimiento": "12",
                "activo": "on",
                "receta-TOTAL_FORMS": "2",
                "receta-INITIAL_FORMS": "0",
                "receta-MIN_NUM_FORMS": "1",
                "receta-MAX_NUM_FORMS": "1000",
                "receta-0-insumo": self.harina.pk,
                "receta-0-cantidad": "500.000",
                "receta-0-unidad": self.gramo.pk,
                "receta-1-insumo": self.harina.pk,
                "receta-1-cantidad": "300.000",
                "receta-1-unidad": self.gramo.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No puedes repetir el mismo insumo")
