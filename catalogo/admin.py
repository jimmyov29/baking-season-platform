from django.contrib import admin

from .models import CategoriaInsumo, Insumo, UnidadMedida


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura", "tipo", "factor_conversion", "unidad_base", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre", "abreviatura")
    ordering = ("tipo", "nombre")



@admin.register(CategoriaInsumo)
class CategoriaInsumoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "unidad_base", "stock_minimo", "activo")
    list_filter = ("categoria", "unidad_base", "activo")
    search_fields = ("nombre", "categoria__nombre")
    autocomplete_fields = ("categoria", "unidad_base")
