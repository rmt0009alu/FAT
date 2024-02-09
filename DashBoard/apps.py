"""
Módulo para la aplicación del DashBoard.
"""
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuración de la app de DashBoard.

    Args:
        AppConfig (django.apps): configurador de aplicaciones
        en Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DashBoard'
