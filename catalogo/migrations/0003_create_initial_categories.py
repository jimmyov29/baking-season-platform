from django.db import migrations


INITIAL_CATEGORIES = ["Ingrediente", "Empaque", "Decoracion", "Otro"]


def create_initial_categories(apps, schema_editor):
    CategoriaInsumo = apps.get_model("catalogo", "CategoriaInsumo")
    for name in INITIAL_CATEGORIES:
        CategoriaInsumo.objects.get_or_create(nombre=name, defaults={"activo": True})


def remove_initial_categories(apps, schema_editor):
    CategoriaInsumo = apps.get_model("catalogo", "CategoriaInsumo")
    CategoriaInsumo.objects.filter(nombre__in=INITIAL_CATEGORIES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0002_add_insumos"),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, remove_initial_categories),
    ]
