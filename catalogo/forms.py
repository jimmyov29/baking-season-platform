from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import CategoriaInsumo, Insumo, Producto, ProductoInsumo, UnidadMedida


class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ("nombre", "abreviatura", "tipo", "factor_conversion", "unidad_base", "activo")
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "abreviatura": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "factor_conversion": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001", "min": "0.000001"}),
            "unidad_base": forms.Select(attrs={"class": "form-select"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = UnidadMedida.objects.filter(activo=True)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        self.fields["unidad_base"].queryset = queryset



class CategoriaInsumoForm(forms.ModelForm):
    class Meta:
        model = CategoriaInsumo
        fields = ("nombre", "activo")
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ("nombre", "categoria", "unidad_base", "stock_minimo", "activo")
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "unidad_base": forms.Select(attrs={"class": "form-select"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "min": "0"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = CategoriaInsumo.objects.filter(activo=True)
        self.fields["unidad_base"].queryset = UnidadMedida.objects.filter(activo=True, unidad_base__isnull=True)



class ProductoForm(forms.ModelForm):
    rendimiento = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )

    class Meta:
        model = Producto
        fields = ("nombre", "descripcion", "precio_venta", "rendimiento", "activo")
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "precio_venta": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "rendimiento": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProductoInsumoForm(forms.ModelForm):
    class Meta:
        model = ProductoInsumo
        fields = ("insumo", "cantidad", "unidad")
        widgets = {
            "insumo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "min": "0.001"}),
            "unidad": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["insumo"].queryset = Insumo.objects.filter(activo=True)
        self.fields["unidad"].queryset = UnidadMedida.objects.filter(activo=True)


class BaseProductoInsumoFormSet(BaseInlineFormSet):
    def clean(self):
        insumos = set()
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or form.cleaned_data.get("DELETE"):
                continue
            insumo = form.cleaned_data.get("insumo")
            if not insumo:
                continue
            if insumo.pk in insumos:
                raise forms.ValidationError("No puedes repetir el mismo insumo en la receta.")
            insumos.add(insumo.pk)
        super().clean()


ProductoInsumoFormSet = inlineformset_factory(
    Producto,
    ProductoInsumo,
    form=ProductoInsumoForm,
    formset=BaseProductoInsumoFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
