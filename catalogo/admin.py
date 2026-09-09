from django.contrib import admin

from .models import UnidadMedida


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura", "tipo", "factor_conversion", "unidad_base", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre", "abreviatura")
    ordering = ("tipo", "nombre")
