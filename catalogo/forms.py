from django import forms

from .models import CategoriaInsumo, Insumo, UnidadMedida


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
