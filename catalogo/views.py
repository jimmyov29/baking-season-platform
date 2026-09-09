from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import InsumoForm, UnidadMedidaForm
from .models import CategoriaInsumo, Insumo, UnidadMedida


class UnidadMedidaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = UnidadMedida
    template_name = "catalogo/unidad_list.html"
    context_object_name = "unidades"
    permission_required = "catalogo.view_unidadmedida"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("unidad_base")
        query = self.request.GET.get("q", "").strip()
        tipo = self.request.GET.get("tipo", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        if query:
            queryset = queryset.filter(Q(nombre__icontains=query) | Q(abreviatura__icontains=query))
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if estado == "activo":
            queryset = queryset.filter(activo=True)
        elif estado == "inactivo":
            queryset = queryset.filter(activo=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos"] = UnidadMedida.Tipo.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "tipo": self.request.GET.get("tipo", ""),
            "estado": self.request.GET.get("estado", ""),
        }
        return context


class UnidadMedidaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = "catalogo/unidad_form.html"
    permission_required = "catalogo.add_unidadmedida"
    success_url = reverse_lazy("catalogo:unidad_list")

    def form_valid(self, form):
        messages.success(self.request, "Unidad de medida creada correctamente.")
        return super().form_valid(form)


class UnidadMedidaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = "catalogo/unidad_form.html"
    permission_required = "catalogo.change_unidadmedida"
    success_url = reverse_lazy("catalogo:unidad_list")

    def form_valid(self, form):
        messages.success(self.request, "Unidad de medida actualizada correctamente.")
        return super().form_valid(form)


class UnidadMedidaToggleActiveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "catalogo.change_unidadmedida"

    def post(self, request, pk):
        unidad = UnidadMedida.objects.get(pk=pk)
        unidad.activo = not unidad.activo
        unidad.save(update_fields=["activo"])
        estado = "activada" if unidad.activo else "desactivada"
        messages.success(request, f"Unidad de medida {estado} correctamente.")
        return redirect("catalogo:unidad_list")



class InsumoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Insumo
    template_name = "catalogo/insumo_list.html"
    context_object_name = "insumos"
    permission_required = "catalogo.view_insumo"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("categoria", "unidad_base")
        query = self.request.GET.get("q", "").strip()
        categoria = self.request.GET.get("categoria", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        if query:
            queryset = queryset.filter(Q(nombre__icontains=query) | Q(categoria__nombre__icontains=query))
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if estado == "activo":
            queryset = queryset.filter(activo=True)
        elif estado == "inactivo":
            queryset = queryset.filter(activo=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = CategoriaInsumo.objects.filter(activo=True)
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "categoria": self.request.GET.get("categoria", ""),
            "estado": self.request.GET.get("estado", ""),
        }
        return context


class InsumoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "catalogo/insumo_form.html"
    permission_required = "catalogo.add_insumo"
    success_url = reverse_lazy("catalogo:insumo_list")

    def form_valid(self, form):
        messages.success(self.request, "Insumo creado correctamente.")
        return super().form_valid(form)


class InsumoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "catalogo/insumo_form.html"
    permission_required = "catalogo.change_insumo"
    success_url = reverse_lazy("catalogo:insumo_list")

    def form_valid(self, form):
        messages.success(self.request, "Insumo actualizado correctamente.")
        return super().form_valid(form)


class InsumoToggleActiveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "catalogo.change_insumo"

    def post(self, request, pk):
        insumo = Insumo.objects.get(pk=pk)
        insumo.activo = not insumo.activo
        insumo.save(update_fields=["activo"])
        estado = "activado" if insumo.activo else "desactivado"
        messages.success(request, f"Insumo {estado} correctamente.")
        return redirect("catalogo:insumo_list")
