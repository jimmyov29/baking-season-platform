from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


INITIAL_UNITS = [
    {"nombre": "gramo", "abreviatura": "g", "tipo": "PESO", "factor_conversion": Decimal("1")},
    {"nombre": "kilogramo", "abreviatura": "kg", "tipo": "PESO", "factor_conversion": Decimal("1000"), "base": "g"},
    {"nombre": "mililitro", "abreviatura": "ml", "tipo": "VOLUMEN", "factor_conversion": Decimal("1")},
    {"nombre": "litro", "abreviatura": "L", "tipo": "VOLUMEN", "factor_conversion": Decimal("1000"), "base": "ml"},
    {"nombre": "unidad", "abreviatura": "und", "tipo": "UNIDAD", "factor_conversion": Decimal("1")},
]


def create_initial_units(apps, schema_editor):
    UnidadMedida = apps.get_model("catalogo", "UnidadMedida")
    created = {}
    for data in INITIAL_UNITS:
        base_abreviatura = data.get("base")
        unidad, _ = UnidadMedida.objects.get_or_create(
            abreviatura=data["abreviatura"],
            defaults={
                "nombre": data["nombre"],
                "tipo": data["tipo"],
                "factor_conversion": data["factor_conversion"],
                "unidad_base": created.get(base_abreviatura),
                "activo": True,
            },
        )
        created[data["abreviatura"]] = unidad


def remove_initial_units(apps, schema_editor):
    UnidadMedida = apps.get_model("catalogo", "UnidadMedida")
    UnidadMedida.objects.filter(abreviatura__in=[unit["abreviatura"] for unit in INITIAL_UNITS]).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UnidadMedida",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True)),
                ("abreviatura", models.CharField(max_length=20, unique=True)),
                ("tipo", models.CharField(choices=[("PESO", "Peso"), ("VOLUMEN", "Volumen"), ("UNIDAD", "Unidad"), ("OTRO", "Otro")], max_length=20)),
                ("factor_conversion", models.DecimalField(decimal_places=6, default=Decimal("1"), max_digits=12)),
                ("activo", models.BooleanField(default=True)),
                (
                    "unidad_base",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="unidades_derivadas",
                        to="catalogo.unidadmedida",
                    ),
                ),
            ],
            options={
                "verbose_name": "unidad de medida",
                "verbose_name_plural": "unidades de medida",
                "ordering": ["tipo", "nombre"],
            },
        ),
        migrations.RunPython(create_initial_units, remove_initial_units),
    ]
