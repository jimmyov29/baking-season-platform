from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("correo electronico", unique=True)
    telefono = models.CharField("telefono", max_length=25, unique=True, blank=True, null=True)
    first_name = models.CharField("nombre", max_length=150, blank=True)
    last_name = models.CharField("apellido", max_length=150, blank=True)
    is_active = models.BooleanField("activo", default=True)
    is_staff = models.BooleanField("staff", default=False)
    date_joined = models.DateTimeField("fecha de registro", default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["email"]
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def clean(self):
        super().clean()
        self.email = BaseUserManager.normalize_email(self.email).lower()
        if self.telefono == "":
            self.telefono = None
        elif self.telefono:
            self.telefono = self.telefono.strip()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.email

    def __str__(self):
        return self.get_full_name()
