from django import forms
from django.contrib.auth.forms import AuthenticationForm, ReadOnlyPasswordHashField

from .models import Usuario


class EmailOrPhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Correo o telefono",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )


class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contrasena", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contrasena", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("email", "telefono", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contrasenas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Contrasena")

    class Meta:
        model = Usuario
        fields = (
            "email",
            "telefono",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
