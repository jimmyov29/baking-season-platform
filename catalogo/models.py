from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class UnidadMedida(models.Model):
    class Tipo(models.TextChoices):
        PESO = "PESO", "Peso"
        VOLUMEN = "VOLUMEN", "Volumen"
        UNIDAD = "UNIDAD", "Unidad"
        OTRO = "OTRO", "Otro"

    nombre = models.CharField(max_length=100, unique=True)
    abreviatura = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    factor_conversion = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1"))
    unidad_base = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="unidades_derivadas",
        blank=True,
        null=True,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["tipo", "nombre"]
        verbose_name = "unidad de medida"
        verbose_name_plural = "unidades de medida"

    def clean(self):
        super().clean()
        if self.factor_conversion <= 0:
            raise ValidationError({"factor_conversion": "El factor de conversion debe ser mayor que cero."})
        if self.pk and self.unidad_base_id == self.pk:
            raise ValidationError({"unidad_base": "Una unidad no puede ser base de si misma."})
        if self.unidad_base and self.unidad_base.tipo != self.tipo:
            raise ValidationError({"unidad_base": "La unidad base debe ser del mismo tipo."})
        if self.unidad_base is None and self.factor_conversion != Decimal("1"):
            raise ValidationError({"factor_conversion": "Una unidad base debe tener factor de conversion 1."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def es_base(self):
        return self.unidad_base_id is None

    @property
    def unidad_base_efectiva(self):
        return self.unidad_base or self

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"



class CategoriaInsumo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoria de insumo"
        verbose_name_plural = "categorias de insumo"

    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    categoria = models.ForeignKey(CategoriaInsumo, on_delete=models.PROTECT, related_name="insumos")
    unidad_base = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name="insumos")
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "insumo"
        verbose_name_plural = "insumos"

    def clean(self):
        super().clean()
        if self.stock_minimo < 0:
            raise ValidationError({"stock_minimo": "El stock minimo no puede ser negativo."})
        if self.unidad_base and not self.unidad_base.es_base:
            raise ValidationError({"unidad_base": "El insumo debe usar una unidad base."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre



class Producto(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    rendimiento = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def clean(self):
        super().clean()
        if self.precio_venta < 0:
            raise ValidationError({"precio_venta": "El precio de venta no puede ser negativo."})
        if self.rendimiento <= 0:
            raise ValidationError({"rendimiento": "El rendimiento debe ser mayor que cero."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class ProductoInsumo(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="insumos_receta")
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name="recetas")
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    unidad = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name="recetas")
    cantidad_base = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal("0"), editable=False)

    class Meta:
        ordering = ["insumo__nombre"]
        constraints = [
            models.UniqueConstraint(fields=["producto", "insumo"], name="unique_insumo_por_producto"),
        ]
        verbose_name = "insumo de producto"
        verbose_name_plural = "insumos de producto"

    def clean(self):
        super().clean()
        if self.cantidad is not None and self.cantidad <= 0:
            raise ValidationError({"cantidad": "La cantidad debe ser mayor que cero."})
        if self.insumo and self.unidad and self.insumo.unidad_base.tipo != self.unidad.tipo:
            raise ValidationError({"unidad": "La unidad debe ser compatible con el insumo."})

    def save(self, *args, **kwargs):
        if self.cantidad is not None and self.unidad_id:
            self.cantidad_base = (self.cantidad * self.unidad.factor_conversion).quantize(Decimal("0.000001"))
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def cantidad_por_unidad(self):
        return self.cantidad_base / Decimal(self.producto.rendimiento)

    def __str__(self):
        return f"{self.producto} - {self.insumo}"
