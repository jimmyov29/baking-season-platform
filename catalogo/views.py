from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import InsumoForm, ProductoForm, ProductoInsumoFormSet, UnidadMedidaForm
from .models import CategoriaInsumo, Insumo, Producto, UnidadMedida


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



class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = "catalogo/producto_list.html"
    context_object_name = "productos"
    permission_required = "catalogo.view_producto"
    paginate_by = 20

    def get_queryset(self):
        queryset = Producto.objects.annotate(num_insumos=Count("insumos_receta")).order_by("nombre")
        query = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        if query:
            queryset = queryset.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))
        if estado == "activo":
            queryset = queryset.filter(activo=True)
        elif estado == "inactivo":
            queryset = queryset.filter(activo=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "estado": self.request.GET.get("estado", ""),
        }
        return context


class ProductoRecipeMixin:
    model = Producto
    form_class = ProductoForm
    template_name = "catalogo/producto_form.html"
    success_url = reverse_lazy("catalogo:producto_list")
    recipe_formset_prefix = "receta"

    def get_formset(self):
        data = self.request.POST if self.request.method == "POST" else None
        return ProductoInsumoFormSet(data=data, instance=self.object, prefix=self.recipe_formset_prefix)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("formset", self.get_formset())
        return context

    def forms_valid(self, form, formset):
        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())

    def forms_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, ProductoRecipeMixin, CreateView):
    permission_required = ("catalogo.add_producto", "catalogo.add_productoinsumo")
    success_message = "Producto creado correctamente."

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.forms_valid(form, formset)
        return self.forms_invalid(form, formset)


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, ProductoRecipeMixin, UpdateView):
    permission_required = ("catalogo.change_producto", "catalogo.change_productoinsumo")
    success_message = "Producto actualizado correctamente."

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.forms_valid(form, formset)
        return self.forms_invalid(form, formset)


class ProductoToggleActiveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "catalogo.change_producto"

    def post(self, request, pk):
        producto = Producto.objects.get(pk=pk)
        producto.activo = not producto.activo
        producto.save(update_fields=["activo"])
        estado = "activado" if producto.activo else "desactivado"
        messages.success(request, f"Producto {estado} correctamente.")
        return redirect("catalogo:producto_list")
