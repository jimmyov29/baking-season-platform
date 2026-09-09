from django.urls import path

from .views import (
    UnidadMedidaCreateView,
    UnidadMedidaListView,
    UnidadMedidaToggleActiveView,
    UnidadMedidaUpdateView,
)


app_name = "catalogo"

urlpatterns = [
    path("unidades/", UnidadMedidaListView.as_view(), name="unidad_list"),
    path("unidades/nueva/", UnidadMedidaCreateView.as_view(), name="unidad_create"),
    path("unidades/<int:pk>/editar/", UnidadMedidaUpdateView.as_view(), name="unidad_update"),
    path("unidades/<int:pk>/estado/", UnidadMedidaToggleActiveView.as_view(), name="unidad_toggle_active"),
]
