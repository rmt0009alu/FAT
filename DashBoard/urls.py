"""
URLs para usar con el DashBoard.
"""
from django.urls import path
from .views import dashboard, nueva_compra, eliminar_compras, nuevo_seguimiento, eliminar_seguimientos


urlpatterns = [
    path('dashboard/', dashboard, name="dashboard"),

    path('dashboard/nueva_compra/', nueva_compra, name="nueva_compra"),

    path('dashboard/eliminar_compras/', eliminar_compras, name="eliminar_compras"),

    path('dashboard/nuevo_seguimiento/', nuevo_seguimiento, name="nuevo_seguimiento"),

    path('dashboard/eliminar_seguimientos/', eliminar_seguimientos, name="eliminar_seguimientos"),
]
