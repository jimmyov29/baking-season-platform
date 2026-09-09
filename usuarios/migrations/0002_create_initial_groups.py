from django.db import migrations


INITIAL_GROUPS = ["ADMINISTRADOR", "VENTAS", "COMPRAS", "PRODUCCION", "SOCIO"]


def create_initial_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in INITIAL_GROUPS:
        Group.objects.get_or_create(name=name)


def remove_initial_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=INITIAL_GROUPS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_groups, remove_initial_groups),
    ]
