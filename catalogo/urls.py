from django.urls import path

from .views import (
    InsumoCreateView,
    ProductoCreateView,
    ProductoListView,
    ProductoToggleActiveView,
    ProductoUpdateView,
    InsumoListView,
    InsumoToggleActiveView,
    InsumoUpdateView,
    UnidadMedidaCreateView,
    UnidadMedidaListView,
    UnidadMedidaToggleActiveView,
    UnidadMedidaUpdateView,
)


app_name = "catalogo"

urlpatterns = [
    path("productos/", ProductoListView.as_view(), name="producto_list"),
    path("productos/nuevo/", ProductoCreateView.as_view(), name="producto_create"),
    path("productos/<int:pk>/editar/", ProductoUpdateView.as_view(), name="producto_update"),
    path("productos/<int:pk>/estado/", ProductoToggleActiveView.as_view(), name="producto_toggle_active"),
    path("insumos/", InsumoListView.as_view(), name="insumo_list"),
    path("insumos/nuevo/", InsumoCreateView.as_view(), name="insumo_create"),
    path("insumos/<int:pk>/editar/", InsumoUpdateView.as_view(), name="insumo_update"),
    path("insumos/<int:pk>/estado/", InsumoToggleActiveView.as_view(), name="insumo_toggle_active"),
    path("unidades/", UnidadMedidaListView.as_view(), name="unidad_list"),
    path("unidades/nueva/", UnidadMedidaCreateView.as_view(), name="unidad_create"),
    path("unidades/<int:pk>/editar/", UnidadMedidaUpdateView.as_view(), name="unidad_update"),
    path("unidades/<int:pk>/estado/", UnidadMedidaToggleActiveView.as_view(), name="unidad_toggle_active"),
]
