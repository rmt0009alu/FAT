"""
Modelos para usar con el DashBoard.
"""
from datetime import timedelta
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone


class StockComprado(models.Model):
    """Modelo para los stocks comprados por el usuario.

    Args:
        models (django.db.models.Model): modelo de Django.
    """
    # Todos los campos serán obligatorios (no permito 'null' ni 'blank')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Notación de guión bajo '_' para la BD
    ticker_bd = models.CharField(max_length=7)

    # Refactoring:
    # ------------
    # 'choices' no me sirve
    # Limito las opciones de los campos de las bases de datos:
    # BD_CHOICES = (
    #     ('BD1', 'dj30'),
    #     ('BD2', 'ibex35'),
    # )
    # bd = models.CharField(max_length=10, choices=BD_CHOICES)
    bd = models.CharField(max_length=10)
    # Notación de punto '.' para mostrar
    ticker = models.CharField(max_length=7)
    nombre_stock = models.CharField(max_length=255)
    # Lo guardo como DateTimeField para que haya
    # correspondencia de tipos con lo que guardo
    # en las bases de datos de los stocks, pero
    # podría ser DateField
    fecha_compra = models.DateTimeField()
    num_acciones = models.PositiveIntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=4)
    moneda = models.CharField(max_length=4)
    sector = models.CharField(max_length=255)
    objects = models.Manager()

    class Meta:
        """Clase interna para agregar atributos especiales como
        restricciones.
        """
        constraints = [
            # Restricción a nivel de BD porque 'choices' sólo limita
            # en la vista de 'admin':
            models.CheckConstraint(
                name='valores_bd',
                check=Q(bd__in=['dj30', 'ibex35']),
            ),
            # Restricción de fechas futuras (tiene que ser menor a mañana)
            models.CheckConstraint(
                name='fecha_compra_no_futura',
                check=models.Q(fecha_compra__lte=timezone.now() + timedelta(days=1)),
            ),
        ]

    def posicion(self):
        """No se guarda como un campo, pero facilita el
        acceso a la información.

        Returns:
            (float): precio por número de acciones = cantidad gastada
        """
        return self.precio_compra * self.num_acciones

    def __str__(self):
        """Método magic para mostrar info. como un string.

        Returns:
            _type_: _description_
        """
        return f"{self.nombre_stock} - {self.usuario} - {self.fecha_compra} - {self.moneda}"


class StockSeguimiento(models.Model):
    """Modelo para los stocks seguidos por el usuario.

    Args:
        models (django.db.models.Model): modelo de Django.
    """
    # Todos los campos serán obligatorios (no permito 'null' ni 'blank')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Notación de guión bajo '_' para la BD
    ticker_bd = models.CharField(max_length=7)
    bd = models.CharField(max_length=10)
    # Notación de punto '.' para mostrar
    ticker = models.CharField(max_length=7)
    nombre_stock = models.CharField(max_length=255)
    fecha_inicio_seguimiento = models.DateTimeField()
    precio_entrada_deseado = models.DecimalField(max_digits=10, decimal_places=4)
    moneda = models.CharField(max_length=4)
    sector = models.CharField(max_length=255)
    objects = models.Manager()

    def __str__(self):
        """Método magic para mostrar info. como un string.

        Returns:
            _type_: _description_
        """
        return f"{self.nombre_stock} - {self.usuario} - {self.moneda}"
